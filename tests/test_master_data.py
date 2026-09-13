from database.connection import get_connection

def test_master_data_rules():
    connection = get_connection()
    try:
        from database.repositories import get_or_create_city
        
        # 1. Distinct Srinagar/Jammu
        srinagar_id = get_or_create_city({
            "name": "Srinagar", "state": "Jammu and Kashmir", "country": "India", "latitude": 34.0, "longitude": 74.0
        }, connection)
        
        jammu_id = get_or_create_city({
            "name": "Jammu", "state": "Jammu and Kashmir", "country": "India", "latitude": 32.0, "longitude": 74.0
        }, connection)
        
        assert srinagar_id != jammu_id
        
        # 2. Idempotency (Chandigarh once)
        chandigarh_id1 = get_or_create_city({
            "name": "Chandigarh", "state": "Chandigarh", "country": "India", "latitude": 30.0, "longitude": 76.0
        }, connection)
        
        chandigarh_id2 = get_or_create_city({
            "name": "Chandigarh", "state": "Chandigarh", "country": "India", "latitude": 30.0, "longitude": 76.0
        }, connection)
        
        assert chandigarh_id1 == chandigarh_id2
        
        # 3. Country is "India"
        from database.repositories import get_city
        chandigarh_row = get_city(connection, chandigarh_id1)
        # get_city returns id, name, country, latitude, longitude
        assert chandigarh_row[3] == "India"
        
        # 4. Same city name in different states (if any ever arise) generates distinct IDs
        # (Though we don't have this in master list, it tests the constraint properly)
        aurangabad_mh_id = get_or_create_city({
            "name": "Aurangabad", "state": "Maharashtra", "country": "India", "latitude": 19.8762, "longitude": 75.3433
        }, connection)
        
        aurangabad_bh_id = get_or_create_city({
            "name": "Aurangabad", "state": "Bihar", "country": "India", "latitude": 24.75, "longitude": 84.37
        }, connection)
        
        assert aurangabad_mh_id != aurangabad_bh_id

    finally:
        connection.close()
