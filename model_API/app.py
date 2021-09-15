# import main Flask class and request object
from flask import Flask, request, make_response
from flask.helpers import send_file, url_for
from werkzeug.utils import redirect
import numpy
from keras.models import load_model
from pandas.io.json import json_normalize
import io
from io import StringIO
import pandas as pd
import csv

# create the Flask app
app = Flask(__name__)

# extraer estos valores para cargarse desde un file externo
min_ = {'Wheel': 1.0,
 'Gap': -0.567,
 'Angle': 68.02080683554713,
 'HT': 0.061,
 'D': 530.62,
 'Qr': -16.425,
 'G': 15.106,
 'Axle': 1.0,
 'H_shifted': 16.814,
 'diffs_km_shifted': 7.0,
 'km_shifted': 8702.0}
max_ = {'Wheel': 16.0,
 'Gap': 1.092,
 'Angle': 79.76519824394309,
 'HT': 1.519,
 'D': 658.73,
 'Qr': 2.423,
 'G': 22.237,
 'Axle': 8.0,
 'H_shifted': 23.558,
 'diffs_km_shifted': 22550.0,
 'km_shifted': 443576.0}

@app.route('/form', methods=['GET', 'POST'])
def form():
    # handle the POST request
    if request.method == 'POST':
        Wheel = float(request.form.get('Wheel'))
        Gap = float(request.form.get('Gap'))
        Angle = float(request.form.get('Angle'))
        HT = float(request.form.get('HT'))
        D = float(request.form.get('D'))
        Qr = float(request.form.get('Qr'))
        G = float(request.form.get('G'))
        Axle = float(request.form.get('Axle'))
        diffs_km_shifted = float(request.form.get('diffs_km_shifted'))
        km_shifted = float(request.form.get('km_shifted'))

        # scaling

        Wheel = (Wheel - min_['Wheel'])/(max_['Wheel'] - min_['Wheel'])
        Gap = (Gap - min_['Gap'])/(max_['Gap'] - min_['Gap'])
        Angle = (Angle - min_['Angle'])/(max_['Angle'] - min_['Angle'])
        HT = (HT - min_['HT'])/(max_['HT'] - min_['HT'])
        D = (D - min_['D'])/(max_['D'] - min_['D'])
        Qr = (Qr - min_['Qr'])/(max_['Qr'] - min_['Qr'])
        G = (G - min_['G'])/(max_['G'] - min_['G'])
        Axle = (Axle - min_['Axle'])/(max_['Axle'] - min_['Axle'])
        diffs_km_shifted = (diffs_km_shifted - min_['diffs_km_shifted'])/(max_['diffs_km_shifted'] - min_['diffs_km_shifted'])
        km_shifted = (km_shifted - min_['km_shifted'])/(max_['km_shifted'] - min_['km_shifted'])

        features = numpy.array([[Wheel, Gap, Angle, HT, D, Qr, G,
                   Axle, diffs_km_shifted, km_shifted]])
        MODEL_PATH = 'models/'
        model = load_model(MODEL_PATH)
        result = model.predict(features)
        result = (result*(max_['H_shifted'] - min_['H_shifted'])) + min_['H_shifted']
        return '''
                  <h2><div style="text-align:left"><font color='blue'>Parameters: </font></div></h2>
                  <h3>The Wheel value is: {}</h3>
                  <h3>The Gap value is: {}</h3>
                  <h3>The Angle value is: {}</h3>
                  <h3>The HT value is: {}</h3>
                  <h3>The D value is: {}</h3>
                  <h3>The Qr value is: {}</h3>
                  <h3>The G value is: {}</h3>
                  <h3>The Axle value is: {}</h3>
                  <h3>The diffs_km_shifted value is: {}</h3>
                  <h3>The km_shifted value is: {}</h3>
                  <h2><div style="text-align:left"><font color='blue'>Prediction: </font></div></h2>
                  <h2>The H value will be: {}</h2>
                  '''.format(Wheel, Gap, Angle, HT, D, Qr, G,
                   Axle, diffs_km_shifted, km_shifted, result[0])

    # otherwise handle the GET request
    return '''
           <form method="POST">
               <div><label>Wheel: <input type="float" name="Wheel"></label></div>
               <div><label>Gap: <input type="float" name="Gap"></label></div>
               <div><label>Angle: <input type="float" name="Angle"></label></div>
               <div><label>HT: <input type="float" name="HT"></label></div>
               <div><label>D: <input type="float" name="D"></label></div>
               <div><label>Qr: <input type="float" name="Qr"></label></div>
               <div><label>G: <input type="float" name="G"></label></div>
               <div><label>Axle: <input type="float" name="Axle"></label></div>
               <div><label>diffs_km_shifted: <input type="float" name="diffs_km_shifted"></label></div>
               <div><label>km_shifted: <input type="float" name="km_shifted"></label></div>
               <input type="submit" value="Submit">
           </form>
           <h3><div style="text-align:left"><font color='blue'>Notes: </font></div></h3>
           <p><h4>Wheel takes values from {} to {} </h4></p>
           <p><h4>Gap takes values from {} to {} </h4></p>
           <p><h4>Angle takes values from {} to {}</h4></p>
           <p><h4>HT takes values from {} to {} </h4></p>
           <p><h4>D takes values from {} to {} </h4></p>
           <p><h4>Qr takes values from {} to {} </h4></p>
           <p><h4>G takes values from {} to {} </h4></p>
           <p><h4>Axle takes values from {} to {} </h4></p>
           <p><h4>diffs_km_shifted takes values from {} to {} </h4></p>
           <p><h4>km_shifted takes values from {} to {} </h4></p>
           '''.format(min_['Wheel'], max_['Wheel'], min_['Gap'], max_['Gap'],min_['Angle'], max_['Angle'],
            min_['HT'], max_['HT'], min_['D'], max_['D'], min_['Qr'], max_['Qr'],
            min_['G'], max_['G'],min_['Axle'], max_['Axle'],min_['diffs_km_shifted'], max_['diffs_km_shifted'],
            min_['km_shifted'], max_['km_shifted'])

@app.route("/", methods=['GET', 'POST'])
def uploadFiles():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        
        if uploaded_file.filename != '':
            file_path = ( "files/file.csv")
            uploaded_file.save(file_path)
        return redirect(url_for('downloadFile'))
        
    return '''
                <h1>Upload your CSV file</h1>
                    <form method="POST" action="" enctype="multipart/form-data">
                    <p><input type="file" name="file"></p>
                    <p><input type="submit" value="Submit"></p>
                    </form>
                </body>
                </html>  '''

@app.route('/download')
def downloadFile ():
    path = "files/file.csv"
    
    MODEL_PATH = 'models/'
    model = load_model(MODEL_PATH)

    predictions=model.predict(pd.read_csv(path, sep=';'))
    df_predictions = pd.DataFrame(predictions)
    df_predictions.to_csv('files/predictions.csv', index=False)
    return send_file("files/predictions.csv", as_attachment=True)

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)