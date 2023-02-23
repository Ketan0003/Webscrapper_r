from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo

logging.basicConfig(filename= 'scrapper.log', level=logging.INFO, format= '%(asctime)s %(message)s')

app = Flask(__name__)

# Home page
@app.route('/', methods =['GET'])
def home_page():
    return render_template('index.html')

# logic page
@app.route('/review', methods = ['POST', 'GET'])
def logic_operation():
    if (request.method == 'POST'):
        try:
            search_bar = request.form['content'].replace(" ","")
            flipkart_url = 'https://www.flipkart.com/search?q=' + search_bar
            url_client = urlopen(flipkart_url)
            flipkart_link = url_client.read()
            url_client.close()
            flipkart_html = bs(flipkart_link, 'html.parser')
            bigbox = flipkart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            box = bigbox[0]
            product_link = 'https://www.flipkart.com' + box.div.div.a['href']
            product_details = requests.get(product_link)
            product_details.encoding='utf-8'
            product_html = bs(product_details.text, 'html.parser')
            print(product_html) 
            comment_box = product_html.find_all("div", {"class":"_16PBlm"}) # for extraction of comments containers

            # for creating the individual CSV file for records
            filename = search_bar + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []

            # looping to extract the details
            for i in comment_box:
                try :
                    logging.info("I am in the name extraction session")
                    # extracting the name
                    name = i.div.div.find_all("p", {"class":"_2sc7ZR _2V5EHH"})[0].text

                except:
                    logging.info("name")

                try:
                    # extracting the ratings
                    rating = i.div.div.div.find_all("div",{"class":"_3LWZlK _1BLPMq"})[0].text  

                except:
                    rating = "No Rating"
                    logging.info("rating")

                try:
                    # comment head
                    commentHead = i.div.div.p.text    

                except:    
                    commentHead = "No comment heading"
                    logging.info("Commment heading")

                try:
                    # details comment
                    detailComment = i.div.div.find_all("div", {"class":""})[0].text    

                except Exception as e:
                    logging.info(e)


                mydict = {"Product": search_bar, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": detailComment}
                reviews.append(mydict)
            logging.info(f"Log my final result {reviews}")


            
            
            client = pymongo.MongoClient("mongodb+srv://ketan_03:Ketan9856trader@cluster0.9epk8xo.mongodb.net/?retryWrites=true&w=majority")
            db = client['Webscrapper_database']
            coll_rec = db['Web_scrapper_coll']
            coll_rec.insert_many(reviews)


            return render_template('result.html', reviews = reviews[0:(len(reviews)-1)])    
        except Exception as e:
            logging.info(e)
            return "Something is wrong"

    # Redirecting to the home page
    else:
        return render_template('index.html')        





if __name__ == "__main__":
    app.run(host='0.0.0.0')
