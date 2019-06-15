.PHONY: loaddb


loaddb:
	heroku pg:backups:capture DATABASE_URL
	heroku pg:backups:download
	pg_restore --verbose --clean --no-acl --no-owner -h localhost -d lapl latest.dump
	rm latest.dump
