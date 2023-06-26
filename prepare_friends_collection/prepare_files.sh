
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


# Use casanova to add a nb_queries column in english1000+ files
casa map 'math.floor(int(row.user_friends) / 5000) + 1' nb_queries english_1000+_friends_chunk1_before_230209.csv > english_1000+_friends_chunk1_before_230209_+nbqueries.csv
casa map 'math.floor(int(row.user_friends) / 5000) + 1' nb_queries english_1000+_friends_chunk2_after_230209.csv > english_1000+_friends_chunk2_after_230209_+nbqueries.csv

# Use casanova to add a cumul_nb_queries column in english1000+ files
casa map -I 'cumul=0' -B 'cumul += int(row.nb_queries)' 'cumul' cumul english_1000+_friends_chunk1_before_230209_+nbqueries.csv > english_1000+_friends_chunk1_before_230209_+cumulqueries.csv
casa map -I 'cumul=0' -B 'cumul += int(row.nb_queries)' 'cumul' cumul english_1000+_friends_chunk2_after_230209_+nbqueries.csv > english_1000+_friends_chunk2_after_230209_+cumulqueries.csv


## PREPARE SPLIT FOR CHUNK 1

# Use casanova to add a partition column in 999- files for chunk1 (for 12 v2 keys)
casa map 'index % 12 + 1' partition english_999-_friends_chunk1_before_230209.csv > english_999-_friends_chunk1_before_230209_+12partitions.csv
# Split 999- files in 12 chunks for each key
xsv partition partition ready --drop --filename 'english_999-_friends_chunk1_before_230209_part_{}.csv' english_999-_friends_chunk1_before_230209_+12partitions.csv

# Resplit chunk1 parts 3,8,12 leftovers into 20 pieces (for 11 v1 keys & 9 v2 keys)
xsv cat rows english_999-_friends_chunk1_before_230209_part_3_leftover.csv english_999-_friends_chunk1_before_230209_part_8_leftover.csv english_999-_friends_chunk1_before_230209_part_12_leftover.csv > english_999-_friends_chunk1_before_230209_part_3-8-12_leftover.csv
casa map 'index % 20 + 1' partition english_999-_friends_chunk1_before_230209_part_3-8-12_leftover.csv > english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_+20partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_{}.csv' english_999-_friends_chunk1_before_230209_part_3-8-12_leftover_+20partitions.csv


# Use casanova to add a partition column in 1000+ files for chunk1 (for 6 v1 keys, based on a total of 132062 cumulative queries / 6 ~= 22010)
casa map 'math.floor(int(row.cumul) / 22500) + 1' partition english_1000+_friends_chunk1_before_230209_+cumulqueries.csv > english_1000+_friends_chunk1_before_230209_+6partitions.csv
# Split 1000+ files chunk1 in 6 chunks for each key
xsv partition partition ready --drop --filename 'english_1000+_friends_chunk1_before_230209_part_{}.csv' english_1000+_friends_chunk1_before_230209_+6partitions.csv

## (UNUSED)
# Resplit chunk5_leftover 
xsv select '!cumul' english_1000+_friends_chunk1_before_230209_part_5_leftover.csv > english_1000+_friends_chunk1_before_230209_part_5_leftover_tmp.csv
casa map -I 'cumul=0' -B 'cumul += int(row.nb_queries)' 'cumul' cumul english_1000+_friends_chunk1_before_230209_part_5_leftover_tmp.csv > english_1000+_friends_chunk1_before_230209_part_5_leftover_+cumulqueries.csv
casa map 'math.floor(int(row.cumul) / 3775) + 1' partition english_1000+_friends_chunk1_before_230209_part_5_leftover_+cumulqueries.csv > english_1000+_friends_chunk1_before_230209_part_5_leftover_+5partitions.csv
xsv partition partition ready --drop --filename 'english_1000+_friends_chunk1_before_230209_part_5_leftover_{}.csv' english_1000+_friends_chunk1_before_230209_part_5_leftover_+5partitions.csv


## PREPARE SPLIT FOR CHUNK 2

# Use casanova to add a partition column in 1000+ files for chunk2 (for 11 v1 keys, based on a total of 149191 cumulative queries / 11 ~= 13562 / 120queries/h ~= 113h)
casa map 'math.floor(int(row.cumul) / 13565) + 1' partition english_1000+_friends_chunk2_after_230209_+cumulqueries.csv > english_1000+_friends_chunk2_after_230209_+11partitions.csv
# Split 1000+ files chunk2 in 11 chunks for each key
xsv partition partition ready --drop --filename 'english_1000+_friends_chunk2_after_230209_part_{}.csv' english_1000+_friends_chunk2_after_230209_+11partitions.csv

# Split 999- file chunk2 in 2 pieces for running with 9 v2 keys a first part in parallel during those 113h (13565 * 9 = 122085), then across all 20 v1/v2 keys after that time
xsv slice -s 0 -l 122085 english_999-_friends_chunk2_after_230209.csv > english_999-_friends_chunk2-1_after_230209.csv 
xsv slice -s 122085 -l 1000000 english_999-_friends_chunk2_after_230209.csv > english_999-_friends_chunk2-2_after_230209.csv 

# Use casanova to add a partition column in 999- files for chunk2-1 (for 9 v2 keys)
casa map 'index % 9 + 1' partition english_999-_friends_chunk2-1_after_230209.csv > english_999-_friends_chunk2-1_after_230209_+9partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk2-1_after_230209_part_{}.csv' english_999-_friends_chunk2-1_after_230209_+9partitions.csv

# Use casanova to add a partition column in 999- files for chunk2-2 (for 9 v2 keys and 11 v1 keys)
casa map 'index % 20 + 1' partition english_999-_friends_chunk2-2_after_230209.csv > english_999-_friends_chunk2-2_after_230209_+20partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk2-2_after_230209_part_{}.csv' english_999-_friends_chunk2-2_after_230209_+20partitions.csv

# Chunk2-1 stopped in the middle due to all dead v2 keys, so extracting done and reassembling leftover with chunk2-2 into chunk2-leftover1+2

head -1 english_999-_friends_chunk2-1_after_230209.csv > english_999-_friends_chunk2-1_after_230209_sort.csv
xsv behead english_999-_friends_chunk2-1_after_230209.csv | sort >> english_999-_friends_chunk2-1_after_230209_sort.csv
head -1 english_999-_friends_chunk2-1_after_230209.csv > english_999-_friends_chunk2-1_after_230209_leftover.csv
diff english_999-_friends_chunk2-1_after_230209_sort.csv english_999-_friends_chunk2-1_after_230209_cut.csv | grep '<' | sed 's/^< //' >> english_999-_friends_chunk2-1_after_230209_leftover.csv

xsv cat rows english_999-_friends_chunk2-1_after_230209_leftover.csv english_999-_friends_chunk2-2_after_230209.csv | xsv sort -s local_time > english_999-_friends_chunk2-leftover1+2_after_230209.csv

# Use casanova to add a partition column in 999- files for chunk2-leftover1+2 (for 11 v1 keys)
casa map 'index % 11 + 1' partition english_999-_friends_chunk2-leftover1+2_after_230209.csv > english_999-_friends_chunk2-leftover1+2_after_230209_+11partitions.csv
xsv partition partition ready --drop --filename 'english_999-_friends_chunk2-leftover1+2_after_230209_part_{}.csv' english_999-_friends_chunk2-leftover1+2_after_230209_+11partitions.csv



