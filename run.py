from market import app

# from gevent import pywsgi
# from wsgiref.simple_server import make_server

if __name__=='__main__':
    app.run(debug=True,port = '5000') 
   