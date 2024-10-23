from flask import Flask, render_template, request
import sys
application = Flask(__name__)

@application.route("/")
def apply():
    return render_template ("apply.html")

@application.route("/products") 
def view_list():
    return render_template("all_products.html")

@application.route("/reviews") 
def view_review():
    return render_template("view_review.html")

@application.route("/mypage") 
def reg_item():
    return render_template("my_page.html")

@application.route("/new_products") 
def reg_review():
    return render_template("new_products.html")

@application.route("/submit_item")
def reg_item_submit_get():
    name=request.args.get("product-name")
    seller=request.args.get("seller-id")
    location=request.args.get("location")
    price=request.args.get("price")
    condition=request.args.get("condition")
    description=request.args.get("description")
    print(name,seller,location,price,condition,description)

@application.route("/submit_item_post", methods=['POST']) 
def reg_item_submit_post():
    image_file=request.files["photo"] 
    image_file.save("static/image/{}".format(image_file.filename))

    data=request.form
    return render_template("result.html", data=data, img_path="static/image/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0')
