#export db_host=
#export db_port=
#export db_user=
#export db_pwd=

chainlit init
mkdir .graphrag
python -m graphrag.index --init --root .graphrag
psql "postgresql://${db_user}:${db_pwd}@${db_host}:${db_port}" -f init.sql