#! python

import spotipy
import pprint
import os, sys
import csv
import spotipy.util as util
from json.decoder import JSONDecodeError
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import tokens

os.environ['SPOTIPY_REDIRECT_URI'] = 'http://google.pl/'
os.environ['SPOTIPY_CLIENT_ID'] = tokens.SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = tokens.SPOTIPY_CLIENT_SECRET

SCOPE = 'user-read-private user-read-playback-state user-modify-playback-state user-library-read playlist-read-private'


class Playlist:
	def __init__ (self, playlist_index, playlist_id, playlist_name, playlist_tracklist):
		self.playlist_index = playlist_index
		self.playlist_id = playlist_id
		self.playlist_name = playlist_name
		self.playlist_tracklist = playlist_tracklist



class Program:
	def __init__ (self, scope):
		self.username = self.get_username()
		self.scope = SCOPE
		self.token = self.get_token()
		self.user = self.set_variables()[0]
		self.sp = self.set_variables()[1]
		self.playlist_list = []
		
	'''Get the username from terminal and return it'''
	def get_username(self):	
		try:
			username = sys.argv[1]
		except IndexError:
			print('\n You need to pass your username as an argument.')

		return username

	'''Get token'''
	def get_token(self): 
		try:
			token = util.prompt_for_user_token(self.username, self.scope)
		except (AttributeError, JSONDecodeError):
			os.remove(f".cache-{self.username}")
			token = util.prompt_for_user_token(self.username, self.scope)

		return token

	'''Set user and sp variables'''
	def set_variables(self): 
		sp = spotipy.Spotify(auth=self.token)
		user = sp.current_user()
		return user, sp

	'''Print basic info about logged user'''
	def print_stuff(self): 
		print(f'\nYour user account information:\n')
		displayName = self.user['display_name']

		for k,v in self.user.items():
			print(f'{k} : {v}')
		print('\nHello ' + displayName +'!\n')

	'''Get list of last 50 saved tracks'''
	def get_tracks(self): # 
		results = self.sp.current_user_saved_tracks(limit=50)
		for idx, item in enumerate(results['items']):
		    track = item['track']
		    print("\nLast 50 saved tracks:\n\n")
		    print(idx, track['artists'][0]['name'], " – ", track['name'])

	'''Creates playlist instances and prints them'''
	def create_playlist_instances(self):
		results = self.sp.user_playlists(self.username, offset=1)
		playlisty = results['items']
		indexy = []
		while results['next']:
			results = self.sp.next(results)
			playlisty.extend(results['items'])
			for idx, item in enumerate(playlisty):
				indexy.append(str(idx))
				playlist_index = idx
				playlist_id = item['id']
				playlist_name = item['name']
				playlist_tracklist = {}
				print(f'PLAYLISTA: - {idx} - {playlist_name}, ID: {playlist_id}')

				playlist_tracks = self.sp.playlist_tracks(playlist_id)
				for track_idx, item in enumerate(playlist_tracks['items']):
					track_data = item['track']
					track_name = track_data['name']
					track_id = track_data['id']
					
					for artist in track_data['artists']:
						artist_id = artist['id']
						artist_name = artist['name']

					playlist_tracklist[track_idx] = [track_id, track_name, artist_name]

				self.playlist_list.append(Playlist(playlist_index, playlist_id, playlist_name, playlist_tracklist))

		options = ['1', '2', '3']
		choice = input('''\n OPTIONS:\n
			1 - Show playlist info\n
			2 - Back to menu\n
			3 - CSV for all playlists\n
			Choose option:   ''')
		if choice not in options:
			return self.options_menu()
		elif choice == '3':
			return self.create_multiple_csv()
		elif choice == '2':
			return self.options_menu()
		elif choice == '1':
			return self.get_playlist_info(playlisty)

	# def show_playlist(self):
	# 	for x in self.playlist_list:
	# 		print(f'''{x.playlist_index}: {x.playlist_name}\n''')
	# 		for k, v in x.playlist_tracklist.items():
	# 			print(f'{k} --- {v[2]} --- by {v[1]} ')
	# 		print('\n\n')
		
	'''Probably not useful anymore'''
	# def get_playlists(self): 
	# 	results = self.sp.user_playlists(self.username, offset=1)
	# 	playlists = results['items']
	# 	print(results)
	# 	indexy = []
	# 	while results['next']:
	# 		results = self.sp.next(results)
	# 		playlists.extend(results['items'])
	# 		for idx, item in enumerate(playlists):
	# 			indexy.append(str(idx))
	# 			for k, v in item.items():
	# 				metki = ['name']
	# 				#print(k)
	# 				if k in metki:
	# 					print(f'{idx} - {v}')
	# 				else:
	# 					continue
		
	# 	options = ['1', '2']
	# 	choice = input('''\n OPTIONS:\n
	# 		1 - Show playlist info\n
	# 		2 - Back to menu\n

	# 		Choose option:   ''')
	# 	if choice not in options:
	# 		return self.options_menu()
	# 	elif choice == '2':
	# 		return self.options_menu()
	# 	elif choice == '1':
	# 		return self.get_playlist_info(results, playlisty)

	'''Get playlist info (especially playlist_id) and direct to fuction showing list of songs in playlist'''
	def get_playlist_info(self, playlisty): 
		choice = input('\nChoose playlist number to show more info:  ')
		for item in self.playlist_list:
			print(type(item.playlist_index))
			if item.playlist_index == int(choice):
			# 	playlist_id = item['id']
				print('\n')
				# for k, v in item.items():  # Prints dictionary of playlist object (for dev use)
				# 	print(f'{k} - {v}')
				playlist_id = str(item.playlist_index)
				return self.show_playlist_tracks(item)	
			else:
				print('Index not found.\n')
				continue

	'''Shows list of songs in given playlist (Artist name, song name, album name and album year release)'''
	def show_playlist_tracks(self, item, all_csv=False): 
		print(item.playlist_name)
		playlist_tracks = self.sp.playlist_tracks(item.playlist_id)
		data_items = playlist_tracks['items']
		#print(data_items)
		while playlist_tracks['next']:
					playlist_tracks = self.sp.next(playlist_tracks)
					data_items.extend(playlist_tracks['items'])
		indexy = []
		id_dict = {}
		for idx, data_item in enumerate(data_items):
			indexy.append(str(idx))
			# Define variables for certain song info
			track_data = data_item['track']
			track_name = track_data['name']
			track_id = track_data['id']
			track_popularity = track_data['popularity']
			track_album = track_data['album']
			track_album_name = track_album['name']
			track_album_release = track_album['release_date']
			track_album_id = track_album['id']			
			track_artists = track_data['artists']
			for artist in track_artists:
				artist_id = artist['id']
				artist_name = artist['name']

			# Append index:id dictionary
			id_dict[str(idx)] = track_id

			# Print song information
			print(f'''{idx}: {artist_name} - {track_name}\nFrom album "{track_album_name}", released on {track_album_release}\n''')
		#print(id_dict)
		#print(indexy)
		if all_csv==False:
			input('Press ENTER... ')
			'''Ask if user wants to get song info'''
			options = ['1', '2', '3']
			print('''\n 		--- OPTIONS ---\n
				1 - Show song info\n
				2 - Save playlist features to CSV file\n
				Anything else - Go back to main menu\n''')

			choice = input('Choose option:   ')
			if choice == '1':
				track_index = input("Choose song index: ")
				if track_index in indexy:
					chosen_track_id = id_dict[track_index]
					return self.show_track_info(chosen_track_id)
				else: 
					print('Index not found.\n')
					return self.show_playlist_tracks(playlist_id)
			elif choice == '2':
				print("Please wait...")
				print("Collecting data...")
				return self.playlist_audio_features(id_dict)
			else:
				return self.options_menu()
		else:
			print("Please wait...")
			print("Collecting data...")
			return self.playlist_audio_features(id_dict, item, all_csv)

	'''Get song data and print some of it'''
	def show_track_info(self, chosen_track_id):
		chosen_track = self.sp.audio_features(chosen_track_id)
		print(f'Your track ID is {chosen_track_id}')
		print(chosen_track)
		print('This feature doesn\'t work yet')
		input('Press ENTER to go back to main menu.')
		return self.options_menu()

	'''Gets a list of features for all tracks in a playlists and makes it possible to save it in CSV file'''
	def playlist_audio_features(self, id_dict, item, all_csv=False):
		needed_keys = ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'id']
		csv_lists = []
		csv_lists.append(needed_keys)
		for index, track_id in id_dict.items():
			track_features_list = []
			track_name = self.sp.track(track_id)['name']
			artist_name = self.sp.track(track_id)['artists'][0]['name']
			# print(f'{track_name}, {artist_name}')
			track_features = self.sp.audio_features(track_id)[0]
			track_features_list.extend([track_name, artist_name])
			for k, v in track_features.items():
				if k in needed_keys:
					track_features_list.append(str(v))
			# print(track_features_list)
			csv_lists.append(track_features_list)
		#print(csv_lists)				
		if all_csv==False:
			print('''\n 		--- OPTIONS ---\n
				1 - Save playlist data to CSV\n
				Anything else - Go back to main menu\n''')
			choice = input('Choose option: ')
			if choice == '1':
				return self.create_playlist_csv(csv_lists)
			else:
				return self.options_menu()
		else:
			return self.create_playlist_csv(csv_lists, item, all_csv=True)

	'''Save CSV file with a name'''
	def create_playlist_csv(self, csv_lists, item, all_csv=False):
		# print(csv_lists)
		if all_csv==False:
			file_name = input('Type file name for CSV file: ')
		else:
			file_name = f"{item.playlist_name}"
		with open(f'./analyzer/data/{file_name}.csv', 'w', encoding='utf8', newline='') as file:
			writer = csv.writer(file)
			writer.writerows(csv_lists)
		print('Saving complete.\n')
		if all_csv==False:
			input('Press KEY to go back to main menu.')
			return self.options_menu()
		else:
			pass

	'''Not working yet'''
	def create_multiple_csv(self):
		for item in self.playlist_list:
			if os.path.isfile(f'./analyzer/data/{item.playlist_name}.csv'):
				print(f"{item.playlist_name} already exported.")
				continue
			else:
				self.show_playlist_tracks(item, all_csv=True)
				print(f"{item.playlist_name}.csv saved.")
		print('ALl playlists exported.\n')
		return self.options_menu()



		# needed_keys = ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'id']

		# for i in self.playlist_list:
		# 	csv_lists = []
		# 	csv_lists.append(needed_keys)
		# 	for k, v in i.playlist_tracklist.items():
		# 		pass

	'''Main options menu'''
	def options_menu(self): # 
		input("\nPress anything to proceed\n")
		os.system('cls')
		options = ['1', '2', '3', '4', '5']
		print('''\n 		--- OPTIONS ---\n
	1 - Show account info\n
	2 - Create playlist instances (testing)\n
	3 - Show last user saved tracks\n
	4 - Show playlists\n
	5 - Exit\n''')
		choice = input('Choose option:   ')
		if choice not in options:
			return self.options_menu()
		elif choice == '1':
			self.print_stuff()
		elif choice == '2':
			self.create_playlist_instances()
		elif choice =='3':
			print('\n')
			self.get_tracks()
		elif choice == '4':
			print('\n')
			return self.get_playlists()
		elif choice == '5':
			return exit()
		input('\nPress ENTER to proceed.')
		return self.options_menu()

	'''Main'''
	def main(self):
		try:
			self.get_username()
		except IndexError:
			print('\n You need to pass your username as an argument.')
			self.get_username()

		self.get_token()
		self.set_variables()
		self.options_menu()

'''----------------------------------------------------------------'''

prg = Program(SCOPE)

if __name__ == '__main__':
	prg.main()