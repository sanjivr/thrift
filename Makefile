default: develop install

develop:
	virtualenv develop
	( \
		source develop/bin/activate; \
		python -m pip install -r requirements.txt; \
	)

install:
	mkdir -p ~/bin
	ln -sf $(realpath ./thrift) ~/bin/
