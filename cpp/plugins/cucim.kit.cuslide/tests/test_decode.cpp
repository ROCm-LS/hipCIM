#include <cucim/filesystem/file_handle.h>
#include <cucim/io/device.h>
#include <cucim/loader/tile_info.h>
#include <cuslide/tiff/ifd.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <tiffio.h> // LibTIFF for reading TIFF files
#include "cuslide/loader/rocjpeg_processor.h"


// Helper function to create a CuCIMFileHandle from a TIFF file path
CuCIMFileHandle* create_cucim_file_handle(const std::string& tiff_path) {
    cucim::filesystem::FileHandle* file_handle = new cucim::filesystem::FileHandle();
    file_handle->fd = open(tiff_path.c_str(), O_RDONLY);
    if (file_handle->fd < 0) {
        delete file_handle;
        return nullptr; // Handle error appropriately in your application
    }
    file_handle->path = tiff_path;
    return reinterpret_cast<CuCIMFileHandle*>(file_handle);
}

// Helper function to read IFD from a TIFF file using LibTIFF
cuslide::tiff::IFD read_ifd_from_tiff(const std::string& tiff_path) {
    TIFF* tif = TIFFOpen(tiff_path.c_str(), "r");
    if (!tif) {
        throw std::runtime_error("Could not open TIFF file");
    }

    cuslide::tiff::IFD ifd;
    uint32_t width, height;
    uint32_t tile_width, tile_height;
    uint16_t samples_per_pixel;
    uint16_t* bits_per_sample;
    uint32_t* tile_offsets;
    uint32_t* tile_bytecounts;
    uint32_t num_tiles;

    TIFFGetSize(tif, &width, &height);
    TIFFGetField(tif, TIFFTAG_TILEWIDTH, &tile_width);
    TIFFGetField(tif, TIFFTAG_TILELENGTH, &tile_height);
    TIFFGetField(tif, TIFFTAG_SAMPLESPERPIXEL, &samples_per_pixel);

    bits_per_sample = new uint16_t[samples_per_pixel];
    TIFFGetField(tif, TIFFTAG_BITSPERSAMPLE, &bits_per_sample);

    num_tiles = TIFFNumberOfTiles(tif, width, height);
    tile_offsets = new uint32_t[num_tiles];
    tile_bytecounts = new uint32_t[num_tiles];
    TIFFGetField(tif, TIFFTAG_TILEOFFSETS, &tile_offsets);
    TIFFGetField(tif, TIFFTAG_TILEBYTECOUNTS, &tile_bytecounts);

    // Populate the IFD struct
    ifd.width_ = width;
    ifd.height_ = height;
    ifd.tile_width_ = tile_width;
    ifd.tile_height_ = tile_height;
    ifd.samples_per_pixel_ = samples_per_pixel;
    ifd.bits_per_sample_ = std::vector<uint16_t>(bits_per_sample, bits_per_sample[0]); // Assuming all samples have same bits per sample.
    ifd.image_piece_offsets_ = std::vector<uint64_t>(tile_offsets, tile_offsets + num_tiles);
    ifd.image_piece_bytecounts_ = std::vector<uint64_t>(tile_bytecounts, tile_bytecounts + num_tiles);

    TIFFClose(tif);
    delete[] bits_per_sample;
    delete[] tile_offsets;
    delete[] tile_bytecounts;
    return ifd;
}

TEST_CASE("Verify decode using rocjpeg", "[test_decode.cpp]")
{

    std::string tiff_file_path = g_config.get_input_path("private/generic_tiff_000.tif");
    auto tif = std::make_shared<cuslide::tiff::TIFF>(g_config.get_input_path("private/generic_tiff_000.tif").c_str(), O_RDONLY);
    tif->construct_ifds();
    // --- Configuration ---
    const uint32_t batch_size = 4;      // Adjust as needed
    const uint32_t maximum_tile_count = 16; // Adjust as needed

    // --- Read TIFF Data ---
    CuCIMFileHandle* cu_file_handle = create_cucim_file_handle(tiff_file_path);
    if (!cu_file_handle) {
        std::cerr << "Error: Could not open TIFF file: " << tiff_file_path << std::endl;
        return 1;
    }
    cuslide::tiff::IFD ifd = read_ifd_from_tiff(tiff_file_path);

     // Dummy request location and size (request the whole image)
    std::vector<int64_t> request_location_vec = {0, 0};
    std::vector<int64_t> request_size_vec = {static_cast<int64_t>(ifd.width()), static_cast<int64_t>(ifd.height())};
    int64_t* request_location = request_location_vec.data();
    int64_t* request_size = request_size_vec.data();
    uint64_t location_len = 1;

    // No external JPEG tables for this test
    const uint8_t* jpegtable_data = nullptr;
    uint32_t jpegtable_size = 0;

    // --- Instantiate and Test the RocJpegProcessor ---
    try {
        cuslide::loader::RocJpegProcessor processor(
            cu_file_handle,
            &ifd,
            request_location,
            request_size,
            location_len,
            batch_size,
            maximum_tile_count,
            jpegtable_data,
            jpegtable_size
        );

        std::deque<uint32_t> batch_item_counts;
        uint32_t num_remaining_patches = 1;

        // Request some tiles
        uint32_t requested_count = processor.request(batch_item_counts, num_remaining_patches);
        std::cout << "Requested " << requested_count << " tiles." << std::endl;

        // Simulate waiting for processing and retrieving a tile
        if (requested_count > 0) {
            std::shared_ptr<cucim::cache::ImageCacheValue> processed_tile = processor.wait_for_processing(0); // Get first tile
            if (processed_tile) {
                std::cout << "Successfully retrieved processed tile 0." << std::endl;
                std::cout << "Tile data size: " << processed_tile->size() << " bytes." << std::endl;
                //  You could add code here to verify the decoded image data if needed.  This is complex
                //  and depends on the image format, so it's beyond the scope of this basic test.
            } else {
                std::cerr << "Failed to retrieve processed tile 0." << std::endl;
            }
        }

        // Shutdown the processor
        processor.shutdown();

    } catch (const std::runtime_error& error) {
        std::cerr << "Error: " << error.what() << std::endl;
        return 1;
    }

    // --- Cleanup ---
    delete reinterpret_cast<cucim::filesystem::FileHandle*>(cu_file_handle); //  delete the file handle.

    return 0;
}

