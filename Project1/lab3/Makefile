#
# makefile for mymod
# 
obj-m +=mymod.o

default:
	$(MAKE) -C /usr/src/linux M=$(PWD) modules
clean:
	rm *.ko
	rm *.0
	rm *.mod.c


