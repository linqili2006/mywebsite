import sys  
  
#Expand Python classes path with your app's path  
sys.path.insert(0, "c:/website")  
sys.path.insert(0, "c:/website/flask/lib64/python2.7/site-packages")  
  
from app import app as application
