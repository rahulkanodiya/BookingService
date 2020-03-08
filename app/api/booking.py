from app.api import bp
from flask import jsonify, request
from app.models import Booking
from flask import url_for
from app import db
from app.api.errors import bad_request
import requests

@bp.route('/bookings/<int:id>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def booking(id):
    #""" Get a booking. """    
    if request.method == 'GET':
        booking = Booking.query.get(id)
        if booking is None:
            return bad_request('Booking id is not valid.')
        response = jsonify(booking.to_dict())
        response.headers['Location'] = url_for('api.booking', id=id)
        return response

    #""" Update booking's details. """
    elif request.method == 'PUT':
        
        booking = Booking.query.get(id)
        if booking is None:
            return bad_request('Booking id is not valid.')
        
        data = request.get_json() or {}        
        
        if 'status' not in data and 'table_id' not in data:
            return bad_request('booking status and table_id missing in the request.')

        booking_changed = False

        if 'status' in data and not booking.status == data['status']:
            if data['status'] in ['cancelled', 'delayed', 'booked']:
                booking.status = data['status']
                booking_changed = True
            else:
                return bad_request('Invalid booking status in the request. Can only be cancelled, delayed or booked')                                

        if 'table_id' in data and not booking.table_id == data['table_id']:
            table = requests.get("http://localhost:5002/api/v1/restaurants/" + str(booking.restr_id) + "/tables/" + data['table_id'])
            if table.status_code != 200:
                return bad_request('table_id does not exist for restaurant_id in the request.')                                
            else:    
                booking.table_id = data['table_id']
                booking_changed = True

        db.session.commit()

        if booking_changed:  
            response = jsonify(booking.to_dict())
        else:
            response = jsonify({"status": 'nothing to change in the booking'})

        response.status_code = 200
        response.headers['Location'] = url_for('api.booking', id=booking.id)
        return response

    #""" Delete a booking. """
    elif request.method == 'DELETE':
        booking = Booking.query.get(id)
        if booking is None:
            return bad_request('Booking id is not valid.')
        data = booking.to_dict()
        db.session.delete(booking)
        db.session.commit()
        return jsonify({"status": 'booking deleted'}), 204

    #""" POST method not allowed on this endpoint. """
    elif request.method == 'POST':
        return bad_request("You cannot create restauarnt on this end point. Use this for a POST request: "+ url_for('api.bookings'))

    else:
        return bad_request("That's a bad request.")

@bp.route('/bookings', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bookings():
    #""" Get All Bookings. """
    if request.method == 'GET':
        bookings = Booking.query.all()
        
        if bookings is None or bookings==[]:
            return bad_request('No bookings exist.')

        else:      
            response = jsonify(
                            {'bookings': [booking.to_dict() for booking in bookings],
                            '_link': url_for('api.bookings')
                            }
                )
            response.headers['Location'] = url_for('api.bookings')
            return response

    elif request.method == 'POST':
        data = request.get_json() or {}

        if 'user_id' not in data and 'restr_id' not in data and 'table_id' not in data:
            return bad_request('user_id, restr_id and table_id was missing in the request.')
        if 'user_id' not in data:
            return bad_request('user_id name was missing in the request.')
        if 'restr_id' not in data:
            return bad_request('restr_id was missing in the request.')
        if 'table_id' not in data:
            return bad_request('table_id was missing in the request.')            

        user = requests.get('http://localhost:5001/api/v1/users/' + data['user_id'])        
        if user.status_code != 200:     
            return bad_request('user_id in the request does not exist.')
        else:    
            user_data = user.json()

        restr = requests.get('http://localhost:5002/api/v1/restaurants/' + data['restr_id'])        
        if restr.status_code != 200:
            return bad_request('restaurant_id in the request does not exist.')                                
        else:    
            restr_data = restr.json()

        table = requests.get("http://localhost:5002/api/v1/restaurants/" + data["restr_id"] + "/tables/" + data['table_id'])
        if table.status_code != 200:
            return bad_request('table_id does not exist for restaurant_id in the request.')                                
        else:    
            table_data = table.json()       
        
        booking = Booking()
        booking.from_dict(data)
        db.session.add(booking)
        db.session.commit()
        response = jsonify(booking.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.booking', id=booking.id)
        return response

    elif request.method == 'PUT':
        return bad_request("You cannot update a booking on this end point. Use this for a PUT request: "+ url_for('api.booking') + "/<id>")

    elif request.method == 'DELETE':
        return bad_request("You cannot delete a booking on this end point. Use this for a DELETE request: "+ url_for('api.booking') + "/<id>")

    else:
        return bad_request("That's a bad request.")