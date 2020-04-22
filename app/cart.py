from flask import Flask, render_template, request
import cx_Oracle
import json
from datetime import datetime

# database credentials
username = 'admin'
password = 'password'
dsn = 'cis550pricetracker.cgcukgcycu5f.us-east-1.rds.amazonaws.com/CIS550DB'
port = 1512

class Cart:
    total = 100000.00