#ifndef CUSLIDE_NVJPEG_PROCESSOR_H
#define CUSLIDE_NVJPEG_PROCESSOR_H
#include <condition_variable>
#include <memory>
#include <mutex>
#include <queue>
#include <unordered_map>
#include <vector>
#include <rocjpeg/rocjpeg.h>
#include <cucim/filesystem/cufile_driver.h>
#include <cucim/filesystem/file_handle.h>
#include <cucim/io/device.h>
#include <cucim/loader/batch_data_processor.h>
#include <cucim/loader/tile_info.h>
#include "cuslide/tiff/ifd.h"

#include <iostream>
#define CHECK_ROCJPEG(call, msg) {                                     	\
    RocJpegStatus rocjpeg_status = (call);                             	\
    if (rocjpeg_status != ROCJPEG_STATUS_SUCCESS) {                    	\
        std::cerr << #call << " returned " << rocJpegGetErrorName(rocjpeg_status) << " at " <<  __FILE__ << ":" << __LINE__ << std::endl;\
        throw std::runtime_error(fmt::format(msg));			\
    }                                                                   \
}
#define CHECK_HIP(call, msg) {                                       	\
    hipError_t hip_status = (call);                                   	\
    if (hip_status != hipSuccess) {                                   	\
        std::cout << "rocJPEG failure: '#" << hip_status << "' at " <<  __FILE__ << ":" << __LINE__ << std::endl;\
        throw std::runtime_error(fmt::format(msg));			\
    }                                                                 	\
}


namespace cuslide::loader
{
class RocJpegProcessor : public cucim::loader::BatchDataProcessor
{
public:
    RocJpegProcessor(CuCIMFileHandle* file_handle,
                    const cuslide::tiff::IFD* ifd,
                    const int64_t* request_location,
                    const int64_t* request_size,
                    uint64_t location_len,
                    uint32_t batch_size,
                    uint32_t maximum_tile_count,
                    const uint8_t* jpegtable_data,
                    uint32_t jpegtable_size);
    ~RocJpegProcessor();
    uint32_t request(std::deque<uint32_t>& batch_item_counts, uint32_t num_remaining_patches) override;
    uint32_t wait_batch(uint32_t index_in_task,
                        std::deque<uint32_t>& batch_item_counts,
                        uint32_t num_remaining_patches) override;
    std::shared_ptr<cucim::cache::ImageCacheValue> wait_for_processing(uint32_t index) override;
    void shutdown() override;
    uint32_t preferred_loader_prefetch_factor();
private:
    void update_file_block_info(const int64_t* request_location, const int64_t* request_size, uint64_t location_len);
    bool stopped_ = false;
    uint32_t preferred_loader_prefetch_factor_ = 2;
    CuCIMFileHandle* file_handle_ = nullptr;
    const cuslide::tiff::IFD* ifd_ = nullptr;
    std::shared_ptr<cucim::filesystem::CuFileDriver> cufile_;
    size_t tile_width_ = 0;
    size_t tile_width_bytes_ = 0;
    size_t tile_height_ = 0;
    size_t tile_raster_nbytes_ = 0;
    size_t file_size_ = 0;
    size_t file_start_offset_ = 0;
    size_t file_block_size_ = 0;
    uint32_t cuda_batch_size_ = 1;

    RocJpegStreamHandle handle_ = nullptr;
    RocJpegOutputFormat output_format_ = ROCJPEG_OUTPUT_RGB;
    RocJpegStatus state_;
    RocJpegBackend backend_ = ROCJPEG_BACKEND_HARDWARE;
    hipStream_t stream_ = nullptr;

    std::vector<RocJpegStreamHandle> stream_handles_; 
    std::vector<RocJpegDecodeParams> decode_params_;


    std::condition_variable cuda_batch_cond_;
    std::unique_ptr<cucim::cache::ImageCache> cuda_image_cache_;
    uint64_t processed_cuda_batch_count_ = 0;
    cucim::loader::TileInfo fetch_after_{ -1, -1, 0, 0 };
    std::deque<uint32_t> cache_tile_queue_;
    std::unordered_map<uint32_t, cucim::loader::TileInfo> cache_tile_map_;

    uint8_t* unaligned_host_ = nullptr;
    uint8_t* aligned_host_ = nullptr;
    uint8_t* unaligned_device_ = nullptr;
    uint8_t* aligned_device_ = nullptr;

    std::vector<RocJpegImage> raw_cuda_inputs_;
    std::vector<size_t> raw_cuda_inputs_len_;
    std::vector<RocJpegImage> raw_cuda_outputs_;
};
} // namespace cuslide::loader
#endif // CUSLIDE_ROCJPEG_PROCESSOR_H

