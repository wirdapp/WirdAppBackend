BACKUP_DIR='/home/osama/db_backup'
FILE_SUFFIX='_pg_backup.sql'
DATABASE='ramadan_comp'
USER='osama'

FILE=`date +"%Y_%m_%d"`${FILE_SUFFIX}

OUTPUT_FILE=${BACKUP_DIR}/${FILE}

# do the database backup (dump)
# use this command for a database server on localhost. add other options if need be.
pg_dump -U ${USER} ${DATABASE} -f ${OUTPUT_FILE}

# gzip the mysql database dump file
gzip $OUTPUT_FILE
