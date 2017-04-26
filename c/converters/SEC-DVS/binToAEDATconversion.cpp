#include <vector>
#define SENSOR_WIDTH 640
#define SENSOR_HEIGHT 480
#include <fstream>
#include <iostream>
struct dvs_event
{
	unsigned int polarity;
	unsigned int sensorid;
	int col;
	int row;
	double ts;
	int type;
	int strength;
	bool accepted;
};

unsigned char swapbits(unsigned char w, int ind1, int ind2)
{
	int pos1 = 1 << ind1;
	int pos2 = 1 << ind2;
	unsigned char val1 = (w&pos1) >> ind1;
	unsigned char val2 = (w&pos2) >> ind2;

	unsigned char zero1 = 255 - (w&pos1);
	unsigned char zero2 = 255 - (w&pos2);

	unsigned char neww = (w&zero1)&zero2;
	neww = (neww | val1 << ind2) | (val2 << ind1);
	return neww;
}

void gen2adapt(unsigned char* p_w, bool bswapbits)
{
	unsigned int w0 = p_w[0];
	unsigned int w1 = p_w[1];
	unsigned int w2 = p_w[2];
	unsigned int w3 = p_w[3];
	if (bswapbits)
	{
		w3 = swapbits(w3, 1, 2);
		w1 = swapbits(w1, 1, 2);
	}
	p_w[0] = w0;
	p_w[1] = w1;
	p_w[2] = w2;
	p_w[3] = w3;
}


int interpretTPGen2(unsigned char w[4])
{
	int timestamp = -1;
	unsigned int w0 = w[0];
	unsigned int w1 = w[1];
	unsigned int w2 = w[2];
	unsigned int w3 = w[3];
	//std::cout<<"here: "<<w0<<" "<<w1<<" "<<w2<<" "<<w3<<std::endl;
	if (w0 == 102)
	{
		timestamp = int((w1 << 16) + (w2 << 8) + w3);
	}
	return timestamp;
}

bool interpretPaddrGen2(unsigned char w[4], std::vector<dvs_event> & dps, int flip, int maxind, int column, int timestamp)
{
	bool success = false;
	unsigned int w0 = w[0];
	unsigned int w1 = w[1];
	unsigned int w2 = w[2];
	unsigned int w3 = w[3];

	if (w0 == 204)
	{
		int base_row = (w1 & 63) * 8 + 1;// bitand(word(mapp(2)), 63) * 8 + 1;
		for (int i = 0; i < 8; i++)
		{
			dvs_event dp;
			if ((w3&(1 << i)) > 0)
			{
				dp.row = base_row + i;
				dp.col = column;
				dp.polarity = 1;
				dp.sensorid = w1 & 128;
				dp.ts = timestamp;

				if (dp.col >= 0 && dp.col <= maxind && flip == 1)
					dp.col = int(maxind - (int)dp.col);
				dps.push_back(dp);
			}
			if ((w2&(1 << i)) > 0)
			{
				dp.row = base_row + i;
				dp.col = column;
				dp.polarity = 0;
				dp.sensorid = w1 & 128;
				dp.ts = timestamp;

				if (dp.col >= 0 && dp.col <= maxind && flip == 1)
					dp.col = int(maxind - (int)dp.col);
				dps.push_back(dp);
			}
		}
		success = true;
	}
	return success;
}

bool interpretPstartGen2(unsigned char w[4], int& column, int& timestamp)
{
	bool success = false;
	unsigned int w0 = w[0];
	unsigned int w1 = w[1];
	unsigned int w2 = w[2];
	unsigned int w3 = w[3];
	if (w0 == 153)
	{
		// 		res.column = word(mapp(4)) + (bitand(word(mapp(3)), 3)*(2 ^ 8));
		// 		res.ts = bitand(word(mapp(3)), 252) / 2 ^ 2 + word(mapp(2)) * 2 ^ 6;
		column = w3 + ((w2 & 3) << 8);
		//		timestamp = ((w3 & 252) >> 2) + (w2 << 6);
		timestamp = ((w1 & 15) << 6) + (w2 >> 2);
		success = true;
	}
	return success;
}

bool interpretPendGen2(unsigned char w[4])
{
	bool success = false;
	unsigned int w0 = w[0];
	unsigned int w1 = w[1];
	unsigned int w2 = w[2];
	unsigned int w3 = w[3];
	if (w0 == 204 && w1 == 255)
	{
		success = true;
	}
	return success;
}

void writeAEDATHeadr(std::ofstream& file)
{
	/*
	#!AER-DAT2.0
	# This is a raw AE data file - do not edit
	# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event
	# Timestamps tick is 1 us
	# created Fri Aug 03 16:29:47 CEST 2012
	*/
	file << "#!AER-DAT2.0" << std::endl;
	file << "# This is a raw AE data file - do not edit" << std::endl;
	file << "# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event" << std::endl;
	file << "# Timestamps tick is 1 us" << std::endl;
	file << "# created CC 2017" << std::endl;

}

void convertBinGen2ToAEDAT(const char* infilename, const char* outfilename, bool swap_bits)
{
	std::ofstream outfile(outfilename);
	std::ifstream infile(infilename, std::ifstream::binary);
	double curr_time = 0.0;
	writeAEDATHeadr(outfile);
	bool changeEndian = false;
	unsigned char buf[4];
	int wordsread = 0;
	while (!infile.eof())
	{
//		std::cerr << "time: "<<curr_time << std::endl;
		infile.read((char*)&buf[0], 4);
//		wordsread++;
//		std::cerr << "wordsread: " << wordsread << std::endl;
		gen2adapt((unsigned char*)&buf[0], swap_bits);

		int time = interpretTPGen2((unsigned char*)&buf[0]);
		static int s_ts = 1000;
		if (time <= 0)
		{
//			std::cerr << "data: " << curr_time << std::endl;
			static int column = -1;
			int timestamp;
			std::vector<dvs_event> dps;
			if (interpretPstartGen2(buf, column, timestamp))
			{
//				std::cerr << "data start " << std::endl;
				if (timestamp < s_ts)
				{
					curr_time += 1.0;
				}
				s_ts = timestamp;
			}
			else if (interpretPendGen2(buf))
			{
			}
			else if (column>-1)
			{
				interpretPaddrGen2(buf, dps, 0, SENSOR_WIDTH - 1, column, timestamp);
//				std::cerr << "data  " << std::endl;
			}

			for (int i = 0; i < dps.size(); i++)
			{
				char tmpbuffer[4];
				tmpbuffer[0] = 0;
				tmpbuffer[1] = 0;
				tmpbuffer[2] = 0;
				tmpbuffer[3] = 0;
				tmpbuffer[0] = dps[i].polarity>0?1:0;
				tmpbuffer[0] = tmpbuffer[0] | ((dps[i].col)&0x7f)<<1;
				tmpbuffer[1] = (dps[i].col >> 7) & 0x7;
				tmpbuffer[1] = tmpbuffer[1] | (dps[i].row&0x1f)<<3;
				tmpbuffer[2] = dps[i].row >> 5;
				tmpbuffer[3] = 0;
// 				std::cerr << dps[i].polarity << " " << dps[i].col << " " << dps[i].row << std::endl;
// 				std::cerr << *((int*)tmpbuffer) << std::endl;
				char buffer[4];
				if (changeEndian)
				{
					buffer[0] = tmpbuffer[3];
					buffer[1] = tmpbuffer[2];
					buffer[2] = tmpbuffer[1];
					buffer[3] = tmpbuffer[0];
				}
				else
				{
					buffer[0] = tmpbuffer[0];
					buffer[1] = tmpbuffer[1];
					buffer[2] = tmpbuffer[2];
					buffer[3] = tmpbuffer[3];
				}

				outfile.write(buffer, 4);

				unsigned int uitimestamp = (unsigned int)(curr_time*1000);
				//std::cerr << uitimestamp << std::endl;
				char* tsp = (char*)&uitimestamp;
				if (changeEndian)
				{
					buffer[0] = tsp[3];
					buffer[1] = tsp[2];
					buffer[2] = tsp[1];
					buffer[3] = tsp[0];
				}
				else
				{
					buffer[0] = tsp[0];
					buffer[1] = tsp[1];
					buffer[2] = tsp[2];
					buffer[3] = tsp[3];
				}
				//memcpy(buffer, &timestap, 4);
				outfile.write(buffer, 4);
				//				outfile.write
			}

		}


	}
	//std::cerr << curr_time << std::endl;
}


void generateArtificialStream(const char* outfilename)
{
	std::ofstream outfile(outfilename);

	writeAEDATHeadr(outfile);
	bool changeEndian = false;
	int duration = 0.1*1000000;
	double dx = 640.0 / duration;
	
	int row1 = 100;
	int row2 = 200;
	int polarity = 1;
	for (double x = 0.0; x < 640.0; x += dx)
	{
		double time = duration*x / 640.0;
		int col = (int)x;
		for (int i = row1; i < row2; i++)
		{
			int row = i;

			char tmpbuffer[4];
			tmpbuffer[0] = 0;
			tmpbuffer[1] = 0;
			tmpbuffer[2] = 0;
			tmpbuffer[3] = 0;
			tmpbuffer[0] = polarity;
			tmpbuffer[0] = tmpbuffer[0] | ((col) & 0x7f) << 1;
			tmpbuffer[1] = (col >> 7) & 0x7;
			tmpbuffer[1] = tmpbuffer[1] | (row & 0x1f) << 3;
			tmpbuffer[2] = row >> 5;
			tmpbuffer[3] = 0;
			// 				std::cerr << dps[i].polarity << " " << dps[i].col << " " << dps[i].row << std::endl;
			// 				std::cerr << *((int*)tmpbuffer) << std::endl;
			char buffer[4];
			if (changeEndian)
			{
				buffer[0] = tmpbuffer[3];
				buffer[1] = tmpbuffer[2];
				buffer[2] = tmpbuffer[1];
				buffer[3] = tmpbuffer[0];
			}
			else
			{
				buffer[0] = tmpbuffer[0];
				buffer[1] = tmpbuffer[1];
				buffer[2] = tmpbuffer[2];
				buffer[3] = tmpbuffer[3];
			}

			outfile.write(buffer, 4);

			unsigned int uitimestamp = (unsigned int)(time);
			//std::cerr << uitimestamp << std::endl;
			char* tsp = (char*)&uitimestamp;
			if (changeEndian)
			{
				buffer[0] = tsp[3];
				buffer[1] = tsp[2];
				buffer[2] = tsp[1];
				buffer[3] = tsp[0];
			}
			else
			{
				buffer[0] = tsp[0];
				buffer[1] = tsp[1];
				buffer[2] = tsp[2];
				buffer[3] = tsp[3];
			}
			//memcpy(buffer, &timestap, 4);
			outfile.write(buffer, 4);

		}


	}

}

int main(int argc, char** argv)
{
	if (argc > 2)
		convertBinGen2ToAEDAT(argv[1], argv[2], 0);
	else
		generateArtificialStream(argv[1]);
}
