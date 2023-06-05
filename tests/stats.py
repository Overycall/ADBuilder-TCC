import argparse
import os
import sys

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='TXT file with stats from ADBuilder module.')
    
    args = parser.parse_args(argv)
    return args


if __name__ == "__main__":

    args = parse_args(sys.argv[1:])

    time = 0
    cpu = 0
    mem = 0

    counter = 0
    
    with open(args.file, "r") as file:
        for line in file:
            counter = counter + 1

            split = line.split(" ")

            # download e extração
            #time = time + float(split[5])
            #cpu = cpu + int(split[9].replace("%", "").replace(",", ""))
            #mem = mem + int(split[12])

            # rotulação e construção
            time = time + float(split[7])
            cpu = cpu + float(split[11].replace("%", "").replace(",", ""))
            mem = mem + float(split[14])

            print("Time: " + str(time/counter) + " s")
            print("CPU: " + str(cpu/counter) + " %")
            print("MEM: " + str(mem/counter) + " KiB")
    
    filename = os.path.basename(args.file)

    print("\n*** " + filename + " *** (Media)\n")

    print("Total: " + str(counter) + " apks\n")
        
    print("Time: " + str(time/counter) + " s")
    print("CPU: " + str(cpu/counter) + " %")
    print("MEM: " + str(mem/counter) + " KiB")