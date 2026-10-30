.PHONY: firmware firmware-test enclosure enclosure-check

firmware:
	idf.py -C firmware -B "$(CURDIR)/build/firmware" -DDEVICE_BOARD=waveshare-standard build

firmware-test:
	bash firmware/test/run.sh

enclosure:
	python hardware/enclosure/source/build_enclosure.py
	python hardware/enclosure/source/check_meshes.py
	python hardware/enclosure/source/render_preview.py

enclosure-check:
	python hardware/enclosure/source/check_meshes.py
