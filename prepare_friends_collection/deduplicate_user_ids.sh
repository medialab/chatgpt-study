
# GERMAN

cd german/complete
ls german_chunk?.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat german_chunk?.csv.unique_userids | sort -u > german_chunks.csv.unique_userids

ls german_chunk*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat german_chunk*results.csv.gz.unique_userids | sort -u > german_chunks_results.csv.gz.unique_userids

echo "user_id" > ../german_unique_userids.csv
cat german_chunks.csv.unique_userids german_chunks_results.csv.gz.unique_userids | sort -u >> ../german_unique_userids.csv
rm -f *.unique_userids
cd ../..

# FRENCH

cd french/complete
ls french_chunk?.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat french_chunk?.csv.unique_userids | sort -u > french_chunks.csv.unique_userids

ls french_chunk*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat french_chunk*results.csv.gz.unique_userids | sort -u > french_chunks_results.csv.gz.unique_userids

echo "user_id" > ../french_unique_userids.csv
cat french_chunks.csv.unique_userids french_chunks_results.csv.gz.unique_userids | sort -u >> ../french_unique_userids.csv
rm -f *.unique_userids
cd ../..

# ASSEMBLE + ZIP

echo "user_id" > german+french_unique_userids.csv
cat german/german_unique_userids.csv french/french_unique_userids.csv | grep -v "^user_id" | sort -u >> german+french_unique_userids.csv

gzip german/german_unique_userids.csv
gzip french/french_unique_userids.csv


casa map 'index % 9 + 1' partition german+french_unique_userids.csv > german+french_unique_userids_+9partitions.csv
xsv partition partition bios --drop --filename 'german+french_unique_userids_part_{}.csv' german+french_unique_userids_+9partitions.csv




# ENGLISH CHUNK 1 1000+

cd english_chunk1/more_1000/complete
ls english_1000+_friends_chunk1_before_230209_part_?.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat english_1000+_friends_chunk1_before_230209_part_?.csv.unique_userids | sort -u > english_1000+_friends_chunk1_before_230209_parts.csv.unique_userids

ls english_1000+_friends_chunk1_before_230209_part_*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat english_1000+_friends_chunk1_before_230209_part_*results.csv.gz.unique_userids | sort -u > english_1000+_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids

echo "user_id" > english_chunk1_1000+_unique_userids.csv
cat english_1000+_friends_chunk1_before_230209_parts.csv.unique_userids english_1000+_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids | sort -u >> english_chunk1_1000+_unique_userids.csv
rm -f *.unique_userids
cd ../../..


gzip english_chunk1/more_1000/complete/english_chunk1_1000+_unique_userids.csv



# ENGLISH CHUNK 1 999-

ls english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_part_?.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_part_?.csv.unique_userids | sort -u > english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_parts.csv.unique_userids

ls english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_part_*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_part_*results.csv.gz.unique_userids | sort -u > english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids

echo "user_id" > english_chunk1/more_1000/complete/english_chunk1_1000+_unique_userids.csv
cat english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_parts.csv.unique_userids english_chunk1/more_1000/complete/english_1000+_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids | sort -u >> english_chunk1/more_1000/complete/english_chunk1_1000+_unique_userids.csv
gzip english_chunk1/more_1000/complete/english_chunk1_1000+_unique_userids.csv
rm -f english_chunk1/more_1000/complete/*.unique_userids


