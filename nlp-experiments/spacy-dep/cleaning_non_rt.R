rm(list=ls())

library(data.table)
library(dplyr)

options(scipen = 999)

cols <- c('id', 'user_id', 'retweeted_id', 'user_description', 'text', 'lang')
###############
# English Set #
###############
setwd('/home/rodrigo/Desktop/ChatGPT Data/collections')

# df_en1 <- fread('chatgpt_english_20221101-20221129.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en2 <- fread('chatgpt_english_20221130-20221231.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en3 <- fread('chatgpt_english_20230101-20230131.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en4 <- fread('chatgpt_english_20230201-20230228.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en5 <- fread('chatgpt_english_20230301_20230327.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en6 <- fread('chatgpt_english_20230328-20230427.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_en7 <- fread('chatgpt_english_20230427_20230515.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))

df_en_all <- rbind(df_en2, df_en3, df_en4,
                   df_en5, df_en6, df_en7)
df_en <-
  df_en_all %>% filter(lang == 'en')
df_en <- df_en[!duplicated(df_en$id),]

df_non_en <-
  df_en_all %>% filter(lang != 'en')
df_non_en <- df_non_en[!duplicated(df_non_en$id),]

##############
# French Set #
##############
setwd('/home/rodrigo/Desktop/ChatGPT Data/collections')

df_fr1 <- fread('chatgpt_french_20221101-20230427.csv.gz', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_fr2 <- fread('chatgpt_french_20230428_20230515.csv.gz', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))

df_fr_all <- rbind(df_fr1, df_fr2)
df_fr <-
  df_fr_all %>% filter(lang == 'fr')
df_fr <- df_fr[!duplicated(df_fr$id),]

df_non_fr <-
  df_fr_all %>% filter(lang != 'fr')
df_non_fr <- df_non_fr[!duplicated(df_non_fr$id),]

##########################
# Non-English-French Set #
##########################
setwd('/home/rodrigo/Desktop/ChatGPT Data/collections')

df_nenf1 <- fread('chatgpt_not-english_not-french_20221101-20230205.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_nenf2 <- fread('chatgpt_not-english_not-french_20221101-20230427.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))
df_nenf3 <- fread('chatgpt_not-english_not-french_20230428_20230515.csv', select = cols, colClasses = c('id' = 'character', 'user_id' = 'character'))

##############################
# Merging Languages Together #
##############################
final_en <-
  rbind(df_en, df_non_fr[df_non_fr$lang == 'en',], 
        df_nenf1[df_nenf1$lang == 'en',], df_nenf2[df_nenf2$lang == 'en',], df_nenf3[df_nenf3$lang == 'en',])
final_en <- final_en[!duplicated(final_en$id), ]
fwrite(final_en[is.na(final_en$retweeted_id),], 'non_rt_english_unique_id_with_text.csv', row.names = F)

final_fr <-
  rbind(df_fr, df_non_en[df_non_en$lang == 'fr',], 
        df_nenf1[df_nenf1$lang == 'fr',], df_nenf2[df_nenf2$lang == 'fr',], df_nenf3[df_nenf3$lang == 'fr',])
final_fr <- final_fr[!duplicated(final_fr$id), ]
fwrite(final_fr[is.na(final_fr$retweeted_id),], '/home/rodrigo/Desktop/ChatGPT Data/NLP - French an German/non_rt_french_unique_id.csv', row.names = F)

final_de <-
  rbind(df_non_en[df_non_en$lang == 'de',], df_non_fr[df_non_fr$lang == 'de',], 
        df_nenf1[df_nenf1$lang == 'de',], df_nenf2[df_nenf2$lang == 'de',], df_nenf3[df_nenf3$lang == 'de',])
final_de <- final_de[!duplicated(final_de$id), ]
fwrite(final_de[is.na(final_de$retweeted_id),], '/home/rodrigo/Desktop/ChatGPT Data/NLP - French an German/non_rt_german_unique_id.csv', row.names = F)
