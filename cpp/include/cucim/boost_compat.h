#ifndef BOOST_COMPAT_H
#define BOOST_COMPAT_H

#include <boost/config.hpp>

#ifdef BOOST_HAS_LONG_LONG
    namespace boost {
        typedef long long long_long_type;
        typedef unsigned long long ulong_long_type;
    }
#endif

#endif // BOOST_COMPAT_H