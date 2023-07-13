
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

echo "user_id" > ../english_chunk1_1000+_unique_userids.csv
cat english_1000+_friends_chunk1_before_230209_parts.csv.unique_userids english_1000+_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids | sort -u >> ../english_chunk1_1000+_unique_userids.csv
gzip ../english_chunk1_1000+_unique_userids.csv
rm -f *.unique_userids
cd ../../..


# ENGLISH CHUNK 1 999-

cd english_chunk1/less_999/complete
ls english_999-_friends_chunk1_before_230209_part_?.csv english_999-_friends_chunk1_before_230209_part_??.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat english_999-_friends_chunk1_before_230209_part_?.csv.unique_userids english_999-_friends_chunk1_before_230209_part_??.csv.unique_userids | sort -u > english_999-_friends_chunk1_before_230209_parts.csv.unique_userids

ls english_999-_friends_chunk1_before_230209_part_*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat english_999-_friends_chunk1_before_230209_part_*results.csv.gz.unique_userids | sort -u > english_999-_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids

echo "user_id" > ../english_chunk1_999-_unique_userids.csv
cat english_999-_friends_chunk1_before_230209_parts.csv.unique_userids english_999-_friends_chunk1_before_230209_parts_results.csv.gz.unique_userids | sort -u >> ../english_chunk1_999-_unique_userids.csv

rm -f *.unique_userids
cd ../../..

# ASSEMBLE + ZIP

cd english_chunk1
echo "user_id" > english_chunk1_before_230209_unique_userids.csv
cat more_1000/english_chunk1_1000+_unique_userids.csv less_999/english_chunk1_999-_unique_userids.csv | grep -v "^user_id" | sort -u >> english_chunk1_before_230209_unique_userids.csv

gzip more_1000/english_chunk1_1000+_unique_userids.csv
gzip less_999/english_chunk1_999-_unique_userids.csv

casa map 'index % 11 + 1' partition english_chunk1_before_230209_unique_userids.csv > english_chunk1_before_230209_unique_userids_+11partitions.csv
cd ..
xsv partition partition bios --drop --filename 'english_chunk1_before_230209_unique_userids_part_{}.csv' english_chunk1/english_chunk1_before_230209_unique_userids_+11partitions.csv




# ENGLISH CHUNK 2 1000+

cd english_chunk2/more_1000

ls english_1000+_friends_chunk2_after_230209_part_?.csv english_1000+_friends_chunk2_after_230209_part_??.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat english_1000+_friends_chunk2_after_230209_part_?.csv.unique_userids english_1000+_friends_chunk2_after_230209_part_??.csv.unique_userids | sort -u > english_1000+_friends_chunk2_after_230209_parts.csv.unique_userids

xsv cat rows english_1000+_friends_chunk2_after_230209_part*_results.csv > english_1000+_friends_chunk2_after_230209_results.csv
gzip *results.csv
ls english_1000+_friends_chunk2_after_230209_part_*results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat english_1000+_friends_chunk2_after_230209_part_*results.csv.gz.unique_userids | sort -u -T tmpsort > english_1000+_friends_chunk2_after_230209_parts_results.csv.gz.unique_userids

echo "user_id" > ../english_chunk2_1000+_unique_userids.csv
cat english_1000+_friends_chunk2_after_230209_parts.csv.unique_userids english_1000+_friends_chunk2_after_230209_parts_results.csv.gz.unique_userids | sort -u -T tmpsort >> ../english_chunk2_1000+_unique_userids.csv
gzip ../english_chunk2_1000+_unique_userids.csv

rm -f *.unique_userids
cd ../..


# ENGLISH CHUNK 2-1 999-

cd english_chunk2/less_999-part1

xsv select user_id complete/english_999-_friends_chunk2-1_after_230209_cut.csv | xsv behead | sort -u > english_999-_friends_chunk2-1_after_230209_cut.csv.unique_userids

zcat english_999-_friends_chunk2-1_after_230209_cut_results.csv.gz | xsv select friend_id | xsv behead | sort -u > english_999-_friends_chunk2-1_after_230209_cut_results.csv.unique_userids

echo "user_id" > english_999-_friends_chunk2-1_after_230209_cut_unique_userids.csv
cat english_999-_friends_chunk2-1_after_230209_cut.csv.unique_userids english_999-_friends_chunk2-1_after_230209_cut_results.csv.unique_userids | sort -u >> english_999-_friends_chunk2-1_after_230209_cut_unique_userids.csv

rm -f *.unique_userids
cd ../..




# ENGLISH CHUNK 2-2 999-

cd english_chunk2/less_999-part2
mkdir tmpsort

ls english_999-_friends_chunk2-leftover1+2_after_230209_part_?.csv english_999-_friends_chunk2-leftover1+2_after_230209_part_??.csv | while read SOURCE_FILE; do
  xsv select user_id $SOURCE_FILE | xsv behead | sort -u > $SOURCE_FILE.unique_userids
done
cat english_999-_friends_chunk2-leftover1+2_after_230209_part_?.csv.unique_userids english_999-_friends_chunk2-leftover1+2_after_230209_part_??.csv.unique_userids | sort -u > english_999-_friends_chunk2-leftover1+2_after_230209_parts.csv.unique_userids

xsv cat rows english_999-_friends_chunk2-leftover1+2_after_230209_part_*_results.csv > english_999-_friends_chunk2-leftover1+2_after_230209_results.csv
gzip *results.csv

ls english_999-_friends_chunk2-leftover1+2_after_230209_part_*_results.csv.gz | while read RESULT_FILE; do
  zcat $RESULT_FILE | xsv select friend_id | xsv behead | sort -u > $RESULT_FILE.unique_userids
done
cat english_999-_friends_chunk2-leftover1+2_after_230209_part_*_results.csv.gz.unique_userids | sort -u -T tmpsort > english_999-_friends_chunk2-leftover1+2_after_230209_parts_results.csv.gz.unique_userids

echo "user_id" > english_999-_friends_chunk2-leftover1+2_after_230209_unique_userids.csv
cat english_999-_friends_chunk2-leftover1+2_after_230209_parts.csv.unique_userids english_999-_friends_chunk2-leftover1+2_after_230209_parts_results.csv.gz.unique_userids | sort -u -T tmpsort >> english_999-_friends_chunk2-leftover1+2_after_230209_unique_userids.csv
gzip english_999-_friends_chunk2-leftover1+2_after_230209_unique_userids.csv

rm -f *.unique_userids
cd ../..


# ASSEMBLE + ZIP

cd english_chunk2
echo "user_id" > english_chunk2_after_230209_unique_userids.csv
cat more_1000/english_1000+_friends_chunk2_after_230209_unique_userids.csv less_999-part1/english_999-_friends_chunk2-1_after_230209_cut_unique_userids.csv less_999-part2/english_999-_friends_chunk2-leftover1+2_after_230209_unique_userids.csv | grep -v "^user_id" | sort -u -T tmpsort >> english_chunk2_after_230209_unique_userids.csv

gzip */english_chunk2*_unique_userids.csv

casa map 'index % 6 + 1' partition english_chunk2_after_230209_unique_userids.csv > english_chunk2_after_230209_unique_userids_+6partitions.csv
cd ..
xsv partition partition bios --drop --filename 'english_chunk2_after_230209_unique_userids_part_{}.csv' english_chunk2/english_chunk2_after_230209_unique_userids_+6partitions.csv

