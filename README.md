# concertmon

A script I use to simplify monitoring concerts in my location. Does the following:

- Fetches my top bands from last.fm removes blacklisted bands
- Checks with BandsInTown API to see if any of them is having a concert in my locaiton
- Checks SongKick API to see if any of them is having a concert in my locaiton
- Scrapes backstage.info and cross-checks the concerts with the list of bands

Apparently Bandsintown only gives API access to bands these days. I have this access for a while, but there doesn't seem to be a way to get access now. If you don't have access, SongKick looks like a good alternative. 

## How to make it work for you 

1. Create an API token on last.fm (https://www.last.fm/api/account/create)
2. Get a SongKick API key (https://www.songkick.com/api_key_requests/new) 
3. Update docker-compose.yml with your API credentials, email, and other settings
4. Optionally, clean up bands_blacklist.txt. If you're like me, you probably listened to a lot of incorrectly tagged tracks over the years - putting them in this list is an easy way to not query BandsInTown with non-existing bands, podcasts, Default Artists and such.
5. Run `make compose` to build the image and run the script.
