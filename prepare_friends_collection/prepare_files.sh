
# Assemble Rodrigo's source files
xsv cat rows source_rodrigo/until_end_jan.csv source_rodrigo/from_beg_feb.csv > english_complete.csv

# Split file between more or less than 1000 friends to split across v1 and v2 API keys
xsv search -s user_friends '....' english_complete.csv > english_1000+_friends.csv
xsv search -v -s user_friends '....' english_complete.csv > english_999-_friends.csv

# First run will be for 9 days with 12 v2 keys and 6 v1 keys, so we will run:
# - 12 * 120 * 24 * 9 = 311040 v2 queries (less than 1000 results/query)
# -  6 * 120 * 24 * 9 = 155520 v1 queries     (up to 5000 results/query)

# Open english_999-_friends.csv to find a line number with a date change around 311040 => 2023-02-09 line 311054
xsv slice -s 0 -l 311054 english_999-_friends.csv > english_999-_friends_chunk1_before_230209.csv 
xsv slice -s 311054 -l 1000000 english_999-_friends.csv > english_999-_friends_chunk2_after_230209.csv 

# Open english_1000+_friends.csv to find the line number corresponding to the same date change => line 19152
xsv slice -s 0 -l 109152 english_1000+_friends.csv > english_1000+_friends_chunk1_before_230209.csv 
xsv slice -s 109152 -l 1000000 english_1000+_friends.csv > english_1000+_friends_chunk2_after_230209.csv 

# Use casanova to add a partition column in 999- files
casa map 'index % 12 + 1' partition english_999-_friends_chunk1_before_230209.csv > english_999-_friends_chunk1_before_230209_+12partitions.csv
casa map 'index % 12 + 1' partition english_999-_friends_chunk2_after_230209.csv > english_999-_friends_chunk2_after_230209_+12partitions.csv
# Split 999- files in 12 chunks for each key
xsv partition partition ready --drop --filename 'english_999-_friends_chunk1_before_230209_part_{}.csv' english_999-_friends_chunk1_before_230209_+12partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk2_after_230209_part_{}.csv' english_999-_friends_chunk2_after_230209_+12partitions.csv

# Resplit chunks 3,8,12 leftovers
xsv cat rows english_999-_friends_chunk1_before_230209_part_3_leftover.csv english_999-_friends_chunk1_before_230209_part_8_leftover.csv english_999-_friends_chunk1_before_230209_part_12_leftover.csv > english_999-_friends_chunk1_before_230209_part_3-8-12_leftover.csv
casa map 'index % 20 + 1' partition english_999-_friends_chunk1_before_230209_part_3-8-12_leftover.csv > english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_+20partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_{}.csv' english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_+20partitions.csv




# Use casanova to add a nb_queries column in english1000+ files
casa map 'math.floor(int(row.user_friends) / 5000) + 1' nb_queries english_1000+_friends_chunk1_before_230209.csv > english_1000+_friends_chunk1_before_230209_+nbqueries.csv
casa map 'math.floor(int(row.user_friends) / 5000) + 1' nb_queries english_1000+_friends_chunk2_after_230209.csv > english_1000+_friends_chunk2_after_230209_+nbqueries.csv

# Use casanova to add a cumul_nb_queries column in english1000+ files
casa map -I 'cumul=0' -B 'cumul += int(row.nb_queries)' 'cumul' cumul english_1000+_friends_chunk1_before_230209_+nbqueries.csv > english_1000+_friends_chunk1_before_230209_+cumulqueries.csv
casa map -I 'cumul=0' -B 'cumul += int(row.nb_queries)' 'cumul' cumul english_1000+_friends_chunk2_after_230209_+nbqueries.csv > english_1000+_friends_chunk2_after_230209_+cumulqueries.csv

# Use casanova to add a partition column in 1000+ files
casa map 'math.floor(int(row.cumul) / 22500) + 1' partition english_1000+_friends_chunk1_before_230209_+cumulqueries.csv > english_1000+_friends_chunk1_before_230209_+12partitions.csv
# Split 1000+ files chunk 1 in 6 chunks for each key
xsv partition partition ready --drop --filename 'english_1000+_friends_chunk1_before_230209_part_{}.csv' english_1000+_friends_chunk1_before_230209_+12partitions.csv

# TODO partition + split 1000+ file chunk 2 across 11 v1 keys

