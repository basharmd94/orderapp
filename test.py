from geopy.geocoders import Nominatim

def get_current_location():
    try:
        # Initialize Nominatim geocoder
        geolocator = Nominatim(user_agent="location_lookup")

        # Using geocoder to get current latitude and longitude
        location = geolocator.geocode("me")
        latitude, longitude = 23.76478518229741, 90.41535256622923
        return latitude, longitude
    except Exception as e:
        print("Error:", e)
        return None, None

def get_location_name(latitude, longitude):
    try:
        # Initialize Nominatim geocoder
        geolocator = Nominatim(user_agent="location_lookup")

        # Perform reverse geocoding
        location_info = geolocator.reverse((latitude, longitude))
        
        # Extract the location name from the response
        location_name = location_info.address
        return location_name
    except Exception as e:
        print("Error:", e)
        return None

def main():
    # Get current location
    latitude, longitude = get_current_location()
    if latitude is not None and longitude is not None:
        print("Latitude:", latitude)
        print("Longitude:", longitude)

        # Get location name
        location_name = get_location_name(latitude, longitude)
        if location_name:
            print("Location Name:", location_name)
        else:
            print("Failed to retrieve location name.")
    else:
        print("Failed to retrieve current location.")

if __name__ == "__main__":
    main()

