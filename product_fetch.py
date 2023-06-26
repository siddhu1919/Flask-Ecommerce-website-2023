import mysql.connector
from mysql.connector import Error
import os
from PIL import Image
import io
import base64
def save_image():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            database='ecommerce-project-2023',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Fetch the image data from the database
            cursor.execute("SELECT image,name FROM product")  # Replace with your query
            image_data  = cursor.fetchall()
            cursor.close()
            connection.close()
            return image_data

            

        print('Images saved successfully')

    except Error as e:
        print('Error:', e)


