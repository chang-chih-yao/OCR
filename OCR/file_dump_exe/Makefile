VENV_ACTIVATE      = /workshop/PCDV/PYTHON_VENV/py310/bin/activate.csh
PYTHON_BIN         = /workshop/PCDV/PYTHON_VENV/py310/bin

.PHONY: clean
clean:
	@if [ -f "file_dump.spec" ]; then \
		echo "rm -f file_dump.spec"; \
		rm -f "file_dump.spec"; \
	else \
		echo "skip: file_dump.spec not found"; \
	fi
	@if [ -f "scripts/__init__.pyc" ]; then \
		echo "rm -f scripts/__init__.pyc"; \
		rm -f "scripts/__init__.pyc"; \
	else \
		echo "skip: scripts/__init__.pyc not found"; \
	fi
	@if [ -d "build_cythonize/" ]; then \
		echo "rm -rf build_cythonize/"; \
		rm -rf build_cythonize/; \
	else \
		echo "skip: build_cythonize/ found"; \
	fi
	@if [ -d "build/" ]; then \
		echo "rm -rf build/"; \
		rm -rf build/; \
	else \
		echo "skip: build/ found"; \
	fi
	@if [ -d "dist/" ]; then \
		echo "rm -rf dist/"; \
		rm -rf dist/; \
	else \
		echo "skip: dist/ found"; \
	fi
	@echo "find and remove all __pycache__ dirs under current tree"; \
	find . -type d -name "__pycache__" -exec rm -rf {} +

build_cython:
	csh -c $(VENV_ACTIVATE) && python setup.py build_ext --inplace
	rm -rf build/
	rm -rf build_cythonize/
	mv scripts/my_func.py tmp/
	mv scripts/my_func.*.so scripts/my_func.so

build_app:
	csh -c $(VENV_ACTIVATE) && pyinstaller -F file_dump.py
	\cp -f dist/file_dump /rsc/R7227/o/file_dump
	chmod 755 /rsc/R7227/o/file_dump
	rm -f scripts/my_func.so
	mv tmp/my_func.py scripts/

build_all: clean build_cython build_app
	@$(MAKE) -s clean
	@echo "DONE"
