#!/usr/bin/python3

from mysql.connector import Error

import includes.dbconn
from includes.dbconn import connection, cursor, get_row, get_rows, pcursor

#########################################

def calculate_championships(owner_id):

	query = f'SELECT season FROM championships WHERE owner_id = {owner_id} ORDER BY season ASC'

	rows = get_rows(query)

	print("owner id " + str(owner_id) + " has " + str(len(rows)) + " championships")

	championships_count = len(rows)

	query = f'UPDATE owners set championships_count = {championships_count} WHERE owner_id = {owner_id}'

	cursor.execute(query)

	connection.commit()

	if championships_count > 0:

		championships_detail = ""

		for row in rows:

			championships_detail += str(row["season"]) + ", "

		championships_detail = championships_detail[:-2]

		query = f'UPDATE owners set championships_detail = "{championships_detail}" WHERE owner_id = {owner_id}'

		cursor.execute(query)

		connection.commit()

def get_best_finish_detail(owner_id, best_finish):

	best_finish_detail = ""

	query = f'SELECT season FROM ownersXseasons WHERE place = {best_finish} AND owner_id = {owner_id} ORDER BY season ASC'

	rows = get_rows(query)

	for row in rows:

		best_finish_detail += str(row['season']) + ", "

	best_finish_detail = best_finish_detail[:-2]

	query = f'UPDATE owners set best_finish_detail = "{best_finish_detail}" WHERE owner_id = {owner_id}'

	cursor.execute(query)

	connection.commit()

def get_money_finish_detail(owner_id):

	query = f'SELECT season, place FROM ownersXseasons WHERE place < 7 AND owner_id = {owner_id}'

	rows = get_rows(query)

	query = f'UPDATE owners SET money_finishes_count = {len(rows)} WHERE owner_id = {owner_id}'

	cursor.execute(query)

	connection.commit()

	money_finish_detail = ""

	for row in rows:

		place_str = ordinal(row["place"])

		money_finish_detail += str(row["season"]) + ' (' + place_str + '), '

	money_finish_detail = money_finish_detail[:-2]

	query = f'UPDATE owners set money_finishes_detail = "{money_finish_detail}" WHERE owner_id = {owner_id}'

	cursor.execute(query)

	connection.commit()

def calculate_ranks(category):

	asc_or_desc = "DESC"

	col = category + "_count"

	rank_col = category + "_rank"

	table = "owners"

	if category == "avg_finish":

		asc_or_desc = "ASC"

		col = "avg_finish"

		table = "owner_stats"

	elif category == "appearances":

		table = "owner_stats"

	elif category == "rating":

		table = "owner_x_rating"

		col = "rating"

	query = f'SELECT {col}, owner_id FROM {table} ORDER BY {col} {asc_or_desc}'

	rows = get_rows(query)

	print(rows)

	rank = 1

	current_val = 0

	i = 0

	for row in rows:

		i = i + 1

		owner_id = row["owner_id"]

		my_val = row[col]

		if current_val == 0:

			current_val = my_val

		elif my_val != current_val:

			rank = i

			current_val = my_val

		query = f'UPDATE owners SET {rank_col} = {rank} WHERE owner_id = {owner_id}'

		cursor.execute(query)

		connection.commit()

def write_descriptions(category):

	rank_col = category + "_rank"

	desc_col = category + "_desc"

	query = f'SELECT owner_id, {rank_col} FROM owners ORDER BY {rank_col}'

	owners = get_rows(query)

	for owner in owners:

		owner_id = owner["owner_id"]

		my_rank = owner[rank_col]

		rank_ord = ordinal(my_rank)

		query = f'SELECT owner_id FROM owners WHERE {rank_col} = {my_rank}'

		rows = get_rows(query)

		if len(rows) > 1:

			other_owners_count = len(rows) - 1

			rank_desc = f'Tied for {rank_ord} with {other_owners_count} other owner'

			if other_owners_count > 1:

				rank_desc += "s"

			rank_desc += "."

		else:

			rank_desc = rank_ord

		query = f'UPDATE owners SET {desc_col} = "{rank_desc}" WHERE owner_id = {owner_id}'

		cursor.execute(query)

		connection.commit()

def ordinal(n):

	s = ('th', 'st', 'nd', 'rd') + ('th',)*10

	v = n%100

	if v > 13:
		return f'{n}{s[v%10]}'
	else:
		return f'{n}{s[v]}'

#########################################

query = "SELECT * FROM owner_stats";

print(query)

owners = get_rows(query)

for owner in owners:

	owner_id = owner["owner_id"]

	calculate_championships(owner_id)

	get_best_finish_detail(owner_id, owner["best_finish"])

	get_money_finish_detail(owner_id)

########################################
# calculate rankings
########################################

categories = ["appearances", "avg_finish", "championships", "money_finishes", "rating"]

for category in categories:

	calculate_ranks(category)

	write_descriptions(category)
