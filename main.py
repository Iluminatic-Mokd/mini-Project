from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, Trade
from dotenv import load_dotenv
from flask import render_template
from datetime import datetime
from flask_bcrypt import Bcrypt
import os


load_dotenv()


app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or 'sqlite:///site.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template(
        "home.html",
        total_trades=52,
        win_rate="63",
        avg_rr=2.4,
        profit="$1,850"
    )

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # login success
            session["user_id"] = user.id
            return redirect("/dashboard")
        else:
            return "Invalid email or password"

    return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # save user
        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/journal")
def journal():

	page = request.args.get("page",1,type=int)

	trades = Trade.query.order_by(
		Trade.date.desc()
	).paginate(page=page,per_page=10)

	return render_template(
		"index.html",
		trades=trades.items,
		page=page
	)
 
 
@app.route("/add", methods=["GET", "POST"])
def add_trade():
    if request.method == "POST":
        date_str = request.form.get("date")
        asset = request.form.get("asset")
        direction = request.form.get("direction")
        entry = float(request.form.get("entry") or 0)
        exit_price = request.form.get("exit")
        stop_loss = request.form.get("stop_loss")
        take_profit = request.form.get("take_profit")
        result = request.form.get("result")
        notes = request.form.get("notes")

        rr = None
        try:
            if stop_loss and take_profit:
                sl = float(stop_loss)
                tp = float(take_profit)
                rr = (tp - entry) / abs(entry - sl) if entry and sl != entry else None
        except ValueError:
            rr = None

        trade = Trade(
            date=datetime.fromisoformat(date_str) if date_str else datetime.utcnow(),
            asset=asset,
            direction=direction,
            entry=entry,
            exit=float(exit_price) if exit_price else None,
            stop_loss=float(stop_loss) if stop_loss else None,
            take_profit=float(take_profit) if take_profit else None,
            rr=rr,
            result=result or "Loss",
            notes=notes,
        )

        db.session.add(trade)
        db.session.commit()

        return redirect(url_for("journal"))

    return render_template("add_trade.html")

@app.route("/analytics")
def analytics():
    # TODO: เตรียมข้อมูล analytics แล้วส่งเข้า template
    return render_template("analytics.html")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))


@app.route("/edit_trade/<int:id>", methods=["GET","POST"])
def edit_trade(id):
    trade = Trade.query.get(id)

    if request.method == "POST":
        trade.asset = request.form.get("asset")
        trade.direction = request.form.get("direction")
        trade.entry = float(request.form.get("entry") or 0)
        trade.exit = float(request.form.get("exit") or 0)
        trade.stop_loss = float(request.form.get("stop_loss") or 0)
        trade.take_profit = float(request.form.get("take_profit") or 0)
        trade.result = request.form.get("result")
        trade.notes = request.form.get("notes")

        db.session.commit()
        return redirect(url_for("journal"))

    return render_template("edit_trade.html", trade=trade)

@app.route("/delete_trade/<int:id>")
def delete_trade(id):

	trade = Trade.query.get(id)

	db.session.delete(trade)

	db.session.commit()

	return redirect(url_for("journal"))

@app.route("/fix-db")
def fix_db():
    from sqlalchemy import text
    db.session.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120);"))
    db.session.commit()
    return "DB fixed"

if __name__ == "__main__":
    app.run(debug=True)

