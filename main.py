import pickle
import time
import pandas as pd
from stravalib.client import Client

client = Client()
MY_STRAVA_CLIENT_ID, MY_STRAVA_CLIENT_SECRET = (
    open("client.secret").read().strip().split(",")
)


print("Client ID and secret read from file")


url = client.authorization_url(
    client_id=MY_STRAVA_CLIENT_ID,
    redirect_uri="localhost:5000/authorization",
    scope=["read_all", "profile:read_all", "activity:read_all"],
)

with open("access_token.pickle", "rb") as f:
    access_token = pickle.load(f)
    if time.time() > access_token["expires_at"]:
        print("Token has expired, will refresh")
        refresh_response = client.refresh_access_token(
            client_id=MY_STRAVA_CLIENT_ID,
            client_secret=MY_STRAVA_CLIENT_SECRET,
            refresh_token=access_token["refresh_token"],
        )
        access_token = refresh_response
        with open("access_token.pickle", "wb") as f:
            pickle.dump(refresh_response, f)
        print("Refreshed token saved to file")
        client.access_token = refresh_response["access_token"]
        client.refresh_token = refresh_response["refresh_token"]
        client.token_expires_at = refresh_response["expires_at"]

    else:
        print(
            "Token still valid, expires at {}".format(
                time.strftime(
                    "%a, %d %b %Y %H:%M:%S %Z",
                    time.localtime(access_token["expires_at"]),
                )
            )
        )
        client.access_token = access_token["access_token"]
        client.refresh_token = access_token["refresh_token"]
        client.token_expires_at = access_token["expires_at"]

print("Latest access token read from file\n\n\n\n")


activities2 = client.get_activities(limit=100)


# a-z order | create new field table with different, better names. ex gear = shoe, maps = polyline etc
fields = [
    "achievement_count",
    "average_cadence",
    "average_heartrate",
    "average_speed",  # currently meters/sec, should be either MM:SS pace or MPH
    "average_temp",  # currently celcius, change to fareignheight (sp?)
    "average_watts",
    "best_efforts",
    "calories",
    "device_name",
    "distance",  # currently meters, should be miles
    "elapsed_time",  # currently in seconds, should be HH:MM:SS
    "gear",
    "kilojoules",
    "laps",  # number of laps
    "map",  # just the polyline
    "max_heartrate",
    "max_speed",  # currently meters/sec, should be either MM:SS pace or MPH
    "max_watts",
    "moving_time",  # currently in seconds, should be HH:MM:SS
    "name",
    "pr_count",
    "sport_type",
    "start_date_local",
    "suffer_score",
    "type",
    "weighted_average_watts",
]


activity_data = []

for activity in activities2:
    id = activity.id
    act = client.get_activity(id, True)
    my_dict = act.to_dict()
    list = []
    for field in fields:  # probably best to use a switch statement instead
        cur = my_dict.get(field)

        if cur:
            match field:
                case "gear":
                    list.append(cur["name"])
                case "best_efforts":
                    list.append(len(cur))
                case "laps":
                    list.append(len(cur))
                case "map":
                    list.append(cur["polyline"])

                case _:
                    list.append(cur)
        else:
            list.append("")

    activity_data.append(list)

    # activity_data.append([my_dict.get(x) for x in fields])

athlete_shoes = client.get_athlete().shoes


df = pd.DataFrame(activity_data, columns=fields)
df.to_csv("data/activities.csv")