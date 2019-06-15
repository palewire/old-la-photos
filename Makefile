.PHONY: loaddb


loaddb:
	heroku pg:backups:capture DATABASE_URL
	heroku pg:backups:download
	dropdb lapl
	createdb lapl
	pg_restore --verbose --create --no-acl --no-owner -h localhost -d lapl latest.dump
	rm latest.dump
