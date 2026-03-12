#ifndef CUFILE_AMD_H
#define CUFILE_AMD_H

#include <sys/types.h> // For size_t, ssize_t, off_t
#include <cucim/cuda_runtime.h>

#ifdef __cplusplus
extern "C" {
#endif


// CUfile error codes
typedef enum {
    CU_FILE_SUCCESS = 0,
    CU_FILE_DRIVER_NOT_INITIALIZED = 1
    // Other CUfile error codes would go here
} CUfileDriverStatus_t;

enum CUfileFileHandleType {
    CU_FILE_HANDLE_TYPE_OPAQUE_FD = 1, /* linux based fd    */
    CU_FILE_HANDLE_TYPE_OPAQUE_WIN32 = 2, /* windows based handle */
    CU_FILE_HANDLE_TYPE_USERSPACE_FS  = 3, /* userspace based FS */
};

// CUfile error struct
typedef struct {
    CUfileDriverStatus_t err; // CUfile driver error code
    CUresult cu_err;          // CUDA driver error code
} CUfileError_t;


typedef struct CUfileDescr_t {
    CUfileFileHandleType type; /* type of file being registered */
    union {
        int fd;             /* Linux   */
        void *handle;       /* Windows */
    } handle;
    //const CUfileFSOps_t *fs_ops;     /* file system operation table */
} CUfileDescr_t;


// CUfile driver properties
typedef struct {
    unsigned int version;            // Driver version
    unsigned int nvfs;               // NVFS support flag
    unsigned int direct_io;          // Direct I/O support flag
    unsigned int max_direct_io_size; // Maximum size for direct I/O operations
    unsigned int max_device_cache_size; // Maximum size for device cache
    // Additional properties would be here
} CUfileDrvProps_t;
typedef void* CUfileHandle_t;
// Function prototypes
CUfileError_t cuFileHandleRegister(CUfileHandle_t* fh, CUfileDescr_t* descr);
void cuFileHandleDeregister(CUfileHandle_t fh);
CUfileError_t cuFileBufRegister(const void* devPtr_base, size_t length, int flags);
CUfileError_t cuFileBufDeregister(const void* devPtr_base);
ssize_t cuFileRead(CUfileHandle_t fh, void* devPtr_base, size_t size, off_t file_offset, off_t devPtr_offset);
ssize_t cuFileWrite(CUfileHandle_t fh, const void* devPtr_base, size_t size, off_t file_offset, off_t devPtr_offset);
CUfileError_t cuFileDriverOpen(void);
CUfileError_t cuFileDriverClose(void);
CUfileError_t cuFileDriverGetProperties(CUfileDrvProps_t* props);
CUfileError_t cuFileDriverSetPollMode(bool poll, size_t poll_threshold_size);
CUfileError_t cuFileDriverSetMaxDirectIOSize(size_t max_direct_io_size);
CUfileError_t cuFileDriverSetMaxCacheSize(size_t max_cache_size);
CUfileError_t cuFileDriverSetMaxPinnedMemSize(size_t max_pinned_size);

#ifdef __cplusplus
}
#endif

#endif // CUFILE_AMD_H