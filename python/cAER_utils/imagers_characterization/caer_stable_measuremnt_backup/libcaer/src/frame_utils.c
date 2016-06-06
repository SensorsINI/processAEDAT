#include "frame_utils.h"

enum pixelColorEnum {
	PXR, PXB, PXG1, PXG2, PXW
};

static void frameUtilsDemosaicFrame(caerFrameEvent colorFrame, caerFrameEvent monoFrame);

static inline enum pixelColorEnum determinePixelColor(enum caer_frame_event_color_filter colorFilter, int32_t x,
	int32_t y) {
	switch (colorFilter) {
		case RGBG:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXB);
				}
				else {
					return (PXG1);
				}
			}
			else {
				if (y & 0x01) {
					return (PXG2);
				}
				else {
					return (PXR);
				}
			}
			break;

		case GRGB:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXG2);
				}
				else {
					return (PXR);
				}
			}
			else {
				if (y & 0x01) {
					return (PXB);
				}
				else {
					return (PXG1);
				}
			}
			break;

		case GBGR:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXG1);
				}
				else {
					return (PXB);
				}
			}
			else {
				if (y & 0x01) {
					return (PXR);
				}
				else {
					return (PXG2);
				}
			}
			break;

		case BGRG:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXR);
				}
				else {
					return (PXG2);
				}
			}
			else {
				if (y & 0x01) {
					return (PXG1);
				}
				else {
					return (PXB);
				}
			}
			break;

		case RGBW:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXB);
				}
				else {
					return (PXG1);
				}
			}
			else {
				if (y & 0x01) {
					return (PXW);
				}
				else {
					return (PXR);
				}
			}
			break;

		case GRWB:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXW);
				}
				else {
					return (PXR);
				}
			}
			else {
				if (y & 0x01) {
					return (PXB);
				}
				else {
					return (PXG1);
				}
			}
			break;

		case WBGR:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXG1);
				}
				else {
					return (PXB);
				}
			}
			else {
				if (y & 0x01) {
					return (PXR);
				}
				else {
					return (PXW);
				}
			}
			break;

		case BWRG:
			if (x & 0x01) {
				if (y & 0x01) {
					return (PXR);
				}
				else {
					return (PXW);
				}
			}
			else {
				if (y & 0x01) {
					return (PXG1);
				}
				else {
					return (PXB);
				}
			}
			break;

		default:
			// Just fall through.
			break;
	}

	// This is impossible (MONO), so just use red pixel value, as good as any.
	return (PXR);
}

static void frameUtilsDemosaicFrame(caerFrameEvent colorFrame, caerFrameEvent monoFrame) {
	uint16_t *colorPixels = caerFrameEventGetPixelArrayUnsafe(colorFrame);
	uint16_t *monoPixels = caerFrameEventGetPixelArrayUnsafe(monoFrame);

	enum caer_frame_event_color_filter colorFilter = caerFrameEventGetColorFilter(monoFrame);
	int32_t lengthY = caerFrameEventGetLengthY(monoFrame);
	int32_t lengthX = caerFrameEventGetLengthX(monoFrame);
	int32_t idxCENTER = 0;
	int32_t idxCOLOR = 0;

	for (int32_t y = 0; y < lengthY; y++) {
		for (int32_t x = 0; x < lengthX; x++) {
			// Calculate all neighbor indexes.
			int32_t idxLEFT = idxCENTER - 1;
			int32_t idxRIGHT = idxCENTER + 1;

			int32_t idxCENTERUP = idxCENTER - lengthX;
			int32_t idxLEFTUP = idxCENTERUP - 1;
			int32_t idxRIGHTUP = idxCENTERUP + 1;

			int32_t idxCENTERDOWN = idxCENTER + lengthX;
			int32_t idxLEFTDOWN = idxCENTERDOWN - 1;
			int32_t idxRIGHTDOWN = idxCENTERDOWN + 1;

			enum pixelColorEnum pixelColor = determinePixelColor(colorFilter, x, y);
			int32_t RComp;
			int32_t GComp;
			int32_t BComp;

			switch (pixelColor) {
				case PXR: {
					// This is a R pixel. It is always surrounded by G and B only.
					RComp = monoPixels[idxCENTER];

					if (y == 0) {
						// First row.
						if (x == 0) {
							// First column.
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxRIGHT]) / 2;
							BComp = monoPixels[idxRIGHTDOWN];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]) / 2;
							BComp = monoPixels[idxLEFTDOWN];
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 3;
							BComp = (monoPixels[idxRIGHTDOWN] + monoPixels[idxLEFTDOWN]) / 2;
						}
					}
					else if (y == (lengthY - 1)) {
						// Last row.
						if (x == 0) {
							// First column.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxRIGHT]) / 2;
							BComp = monoPixels[idxRIGHTUP];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxLEFT]) / 2;
							BComp = monoPixels[idxLEFTUP];
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 3;
							BComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP]) / 2;
						}
					}
					else {
						// In-between rows.
						if (x == 0) {
							// First column.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxRIGHT]) / 3;
							BComp = (monoPixels[idxRIGHTUP] + monoPixels[idxRIGHTDOWN]) / 2;
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]) / 3;
							BComp = (monoPixels[idxLEFTUP] + monoPixels[idxLEFTDOWN]) / 2;
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]
								+ monoPixels[idxRIGHT]) / 4;
							BComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP] + monoPixels[idxRIGHTDOWN]
								+ monoPixels[idxLEFTDOWN]) / 4;
						}
					}

					break;
				}

				case PXB: {
					// This is a B pixel. It is always surrounded by G and R only.
					BComp = monoPixels[idxCENTER];

					if (y == 0) {
						// First row.
						if (x == 0) {
							// First column.
							RComp = monoPixels[idxRIGHTDOWN];
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxRIGHT]) / 2;
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = monoPixels[idxLEFTDOWN];
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]) / 2;
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxRIGHTDOWN] + monoPixels[idxLEFTDOWN]) / 2;
							GComp = (monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 3;
						}
					}
					else if (y == (lengthY - 1)) {
						// Last row.
						if (x == 0) {
							// First column.
							RComp = monoPixels[idxRIGHTUP];
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxRIGHT]) / 2;
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = monoPixels[idxLEFTUP];
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxLEFT]) / 2;
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP]) / 2;
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 3;
						}
					}
					else {
						// In-between rows.
						if (x == 0) {
							// First column.
							RComp = (monoPixels[idxRIGHTUP] + monoPixels[idxRIGHTDOWN]) / 2;
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxRIGHT]) / 3;
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = (monoPixels[idxLEFTUP] + monoPixels[idxLEFTDOWN]) / 2;
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]) / 3;
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP] + monoPixels[idxRIGHTDOWN]
								+ monoPixels[idxLEFTDOWN]) / 4;
							GComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN] + monoPixels[idxLEFT]
								+ monoPixels[idxRIGHT]) / 4;
						}
					}

					break;
				}

				case PXG1: {
					// This is a G1 (first green) pixel. It is always surrounded by all of R, G, B.
					GComp = monoPixels[idxCENTER];

					if (y == 0) {
						// First row.
						BComp = monoPixels[idxCENTERDOWN];

						if (x == 0) {
							// First column.
							RComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else if (y == (lengthY - 1)) {
						// Last row.
						BComp = monoPixels[idxCENTERUP];

						if (x == 0) {
							// First column.
							RComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else {
						// In-between rows.
						BComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN]) / 2;

						if (x == 0) {
							// First column.
							RComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							RComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							RComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}

					break;
				}

				case PXG2: {
					// This is a G2 (second green) pixel. It is always surrounded by all of R, G, B.
					GComp = monoPixels[idxCENTER];

					if (y == 0) {
						// First row.
						RComp = monoPixels[idxCENTERDOWN];

						if (x == 0) {
							// First column.
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							BComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else if (y == (lengthY - 1)) {
						// Last row.
						RComp = monoPixels[idxCENTERUP];

						if (x == 0) {
							// First column.
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							BComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else {
						// In-between rows.
						RComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN]) / 2;

						if (x == 0) {
							// First column.
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							BComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}

					break;
				}

				case PXW: {
					// This is a W pixel, modified Bayer pattern instead of G2. It is always surrounded by all of R, G, B.
					// TODO: how can W itself contribute to the three colors?
					if (y == 0) {
						// First row.
						RComp = monoPixels[idxCENTERDOWN];

						if (x == 0) {
							// First column.
							GComp = monoPixels[idxRIGHTDOWN];
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = monoPixels[idxLEFTDOWN];
							BComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxRIGHTDOWN] + monoPixels[idxLEFTDOWN]) / 2;
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else if (y == (lengthY - 1)) {
						// Last row.
						RComp = monoPixels[idxCENTERUP];

						if (x == 0) {
							// First column.
							GComp = monoPixels[idxRIGHTUP];
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = monoPixels[idxLEFTUP];
							BComp = monoPixels[idxRIGHT];
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP]) / 2;
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}
					else {
						// In-between rows.
						RComp = (monoPixels[idxCENTERUP] + monoPixels[idxCENTERDOWN]) / 2;

						if (x == 0) {
							// First column.
							GComp = (monoPixels[idxRIGHTUP] + monoPixels[idxRIGHTDOWN]) / 2;
							BComp = monoPixels[idxRIGHT];
						}
						else if (x == (lengthX - 1)) {
							// Last column.
							GComp = (monoPixels[idxLEFTUP] + monoPixels[idxLEFTDOWN]) / 2;
							BComp = monoPixels[idxLEFT];
						}
						else {
							// In-between columns.
							GComp = (monoPixels[idxRIGHTUP] + monoPixels[idxLEFTUP] + monoPixels[idxRIGHTDOWN]
								+ monoPixels[idxLEFTDOWN]) / 4;
							BComp = (monoPixels[idxLEFT] + monoPixels[idxRIGHT]) / 2;
						}
					}

					break;
				}
			}

			// Set color frame pixel values for all color channels.
			colorPixels[idxCOLOR] = U16T(RComp);
			colorPixels[idxCOLOR + 1] = U16T(GComp);
			colorPixels[idxCOLOR + 2] = U16T(BComp);

			// Go to next pixel.
			idxCENTER++;
			idxCOLOR += RGB;
		}
	}
}

caerFrameEventPacket caerFrameUtilsDemosaic(caerFrameEventPacket framePacket) {
	if (framePacket == NULL) {
		return (NULL);
	}

	int32_t countValid = 0;
	int32_t maxLengthX = 0;
	int32_t maxLengthY = 0;

	// This only works on valid frames coming from a camera: only one color channel,
	// but with color filter information defined.
	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		if (caerFrameEventGetChannelNumber(caerFrameIteratorElement) == GRAYSCALE
			&& caerFrameEventGetColorFilter(caerFrameIteratorElement) != MONO) {
			countValid++;

			if (caerFrameEventGetLengthX(caerFrameIteratorElement) > maxLengthX) {
				maxLengthX = caerFrameEventGetLengthX(caerFrameIteratorElement);
			}

			if (caerFrameEventGetLengthY(caerFrameIteratorElement) > maxLengthY) {
				maxLengthY = caerFrameEventGetLengthY(caerFrameIteratorElement);
			}
		}
	CAER_FRAME_ITERATOR_VALID_END

	// Allocate new frame with RGB channels to hold resulting color image.
	caerFrameEventPacket colorFramePacket = caerFrameEventPacketAllocate(countValid,
		caerEventPacketHeaderGetEventSource(&framePacket->packetHeader),
		caerEventPacketHeaderGetEventTSOverflow(&framePacket->packetHeader), maxLengthX, maxLengthY, RGB);
	if (colorFramePacket == NULL) {
		return (NULL);
	}

	int32_t colorIndex = 0;

	// Now that we have a valid new color frame packet, we can convert the frames one by one.
	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		if (caerFrameEventGetChannelNumber(caerFrameIteratorElement) == GRAYSCALE
			&& caerFrameEventGetColorFilter(caerFrameIteratorElement) != MONO) {
			// If all conditions are met, copy from framePacket's mono frame to colorFramePacket's RGB frame.
			caerFrameEvent colorFrame = caerFrameEventPacketGetEvent(colorFramePacket, colorIndex++);

			// First copy all the metadata.
			caerFrameEventSetColorFilter(colorFrame, caerFrameEventGetColorFilter(caerFrameIteratorElement));
			caerFrameEventSetLengthXLengthYChannelNumber(colorFrame, caerFrameEventGetLengthX(caerFrameIteratorElement),
				caerFrameEventGetLengthY(caerFrameIteratorElement), RGB, colorFramePacket);
			caerFrameEventSetPositionX(colorFrame, caerFrameEventGetPositionX(caerFrameIteratorElement));
			caerFrameEventSetPositionY(colorFrame, caerFrameEventGetPositionY(caerFrameIteratorElement));
			caerFrameEventSetROIIdentifier(colorFrame, caerFrameEventGetROIIdentifier(caerFrameIteratorElement));
			caerFrameEventSetTSStartOfFrame(colorFrame, caerFrameEventGetTSStartOfFrame(caerFrameIteratorElement));
			caerFrameEventSetTSEndOfFrame(colorFrame, caerFrameEventGetTSEndOfFrame(caerFrameIteratorElement));
			caerFrameEventSetTSStartOfExposure(colorFrame,
				caerFrameEventGetTSStartOfExposure(caerFrameIteratorElement));
			caerFrameEventSetTSEndOfExposure(colorFrame, caerFrameEventGetTSEndOfExposure(caerFrameIteratorElement));

			// Then the actual pixels.
			frameUtilsDemosaicFrame(colorFrame, caerFrameIteratorElement);

			// Finally validate the new frame.
			caerFrameEventValidate(colorFrame, colorFramePacket);
		}
	CAER_FRAME_ITERATOR_VALID_END

	return (colorFramePacket);
}

void caerFrameUtilsContrast(caerFrameEventPacket framePacket) {
	if (framePacket == NULL) {
		return;
	}

	// O(x, y) = alpha * I(x, y) + beta, where alpha maximizes the range
	// (contrast) and beta shifts it so lowest is zero (brightness).
	// Only works with grayscale images currently. Doing so for color (RGB/RGBA) images would require
	// conversion into another color space that has an intensity channel separate from the color
	// channels, such as Lab or YCrCb. The same algorithm would then be applied on the intensity only.
	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		if (caerFrameEventGetChannelNumber(caerFrameIteratorElement) == GRAYSCALE) {
			uint16_t *pixels = caerFrameEventGetPixelArrayUnsafe(caerFrameIteratorElement);
			int32_t lengthY = caerFrameEventGetLengthY(caerFrameIteratorElement);
			int32_t lengthX = caerFrameEventGetLengthX(caerFrameIteratorElement);

			// On first pass, determine minimum and maximum values.
			int32_t minValue = INT32_MAX;
			int32_t maxValue = INT32_MIN;

			for (int32_t idx = 0; idx < (lengthY * lengthX); idx++) {
				if (pixels[idx] < minValue) {
					minValue = pixels[idx];
				}

				if (pixels[idx] > maxValue) {
					maxValue = pixels[idx];
				}
			}

			// Use min/max to calculate input range.
			int32_t range = maxValue - minValue;

			// Calculate alpha (contrast).
			float alpha = ((float) UINT16_MAX) / ((float) range);

			// Calculate beta (brightness).
			float beta = ((float) -minValue) * alpha;

			// Apply alpha and beta to pixels array.
			for (int32_t idx = 0; idx < (lengthY * lengthX); idx++) {
				pixels[idx] = U16T(alpha * ((float ) pixels[idx]) + beta);
			}
		}
		else {
			caerLog(CAER_LOG_WARNING, "caerFrameUtilsContrast()",
				"Standard contrast enhancement only works with grayscale images. For color image support, please use caerFrameUtilsOpenCVContrast().");
		}
	CAER_FRAME_ITERATOR_VALID_END
}

void caerFrameUtilsWhiteBalance(caerFrameEventPacket framePacket) {

}
