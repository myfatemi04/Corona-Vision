'''
# FEATURES THAT I'M PLANNING TO REMOVE #
@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	email = request.form.get("email")
	firstname = request.form.get("firstname")
	lastname = request.form.get("lastname")
	password_encrypt = generate_password_hash(request.form.get("password"))
	
	if not all(
		(
			firstname,
			lastname,
			email,
			request.form.get("password")
		)
	):
		return render_template("register.html", message="Please fill out all fields")
	
	if corona_sql.find_email(email):
		return render_template("register.html", message="Username already taken")
	
	new_user = corona_sql.User(
		firstname=firstname,
		lastname=lastname,
		email=email,
		password_encrypt=password_encrypt,
		
	)
	
	corona_sql.db.session.add(new_user)
	corona_sql.db.session.commit()
	
	session['email'] = email
	
	return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	
	email = request.form.get("email")
	password = request.form.get("password")
	
	user = corona_sql.find_email(email)
	
	if not user:
		return render_template("login.html", message="Username or password is incorrect")
	
	if check_password_hash(user.password_encrypt, password):
		session['email'] = user.email
		return redirect("/")
	else:
		return render_template("login.html", message="Username or password is incorrect")

@app.route("/logout")
def logout():
	if 'email' in session:
		del session['email']
		
	return redirect("/")


@app.route("/submit_data_csv", methods=['GET', 'POST'])
def submit_data_csv():
	if request.method == 'GET':
		return render_template("submit_data_csv.html")
	else:
		if 'data' not in request.files:
			return render_template("submit_data_csv.html", message="Please attach a file")
			
		file = request.files['data']
		filename = "./data_uploads/" + str(time.time()) + file.filename
		file.save(filename)
		
		return render_template("submit_data_csv_complete.html")
@app.route("/submit_data", methods=['GET', 'POST'])
def submit_data():
	if request.method == 'GET':
		return render_template("submit_data_manual.html")
	else:
		location = request.form.get("location")
		latitude = request.form.get("latitude")
		longitude = request.form.get("longitude")
		confirmed = request.form.get("confirmed")
		recovered = request.form.get("recovered")
		dead = request.form.get("dead")
		email = request.form.get("email")
		if not all((location, latitude, longitude, confirmed, recovered, dead, email)):
			return abort(400)
		
		datapoint = corona_sql.Datapoint(
			location=location,
			latitude=latitude,
			longitude=longitude,
			confirmed=confirmed,
			recovered=recovered,
			dead=dead,
			email=email,
			status=0
		)
		corona_sql.db.session.add(datapoint)
		corona_sql.db.session.commit()
		return "", 200

@app.route("/approve_data", methods=['GET', 'POST'])
def approve_data():
	if 'email' not in session:
		return abort(403)
		
	if request.method == 'GET':
		pending_data = corona_sql.find_pending()
		return render_template("approve_data.html", pending_data=pending_data)
	else:
		data_id = request.form.get("data_id")
		if not data_id:
			return abort(400)
		
		
		found_data = corona_sql.Datapoint.query.filter(corona_sql.Datapoint.data_id == data_id).first()
		if not found_data:
			return abort(400)
		
		previous_datapoints = corona_sql.Datapoint.query.filter(
			and_(
				corona_sql.Datapoint.location == found_data.location,
				corona_sql.Datapoint.status == 1  # old data that was approved
			)
		).all()
		
		for old_data in previous_datapoints:
			corona_sql.db.session.delete(old_data)
		
		
		found_data.status = 1
		corona_sql.db.session.commit()
		return "", 200
'''
