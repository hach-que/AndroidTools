/*
 * Copyright (C) 2008 The Android Open Source Project
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */
#ifndef _LOCALE_H_
#define _LOCALE_H_

#include <sys/cdefs.h>
#if __HACK_BUILTIN_LOCALECONV
#include <sys/limits.h>
#endif

__BEGIN_DECLS

enum {
    LC_CTYPE     = 0,
    LC_NUMERIC   = 1,
    LC_TIME      = 2,
    LC_COLLATE   = 3,
    LC_MONETARY  = 4,
    LC_MESSAGES  = 5,
    LC_ALL       = 6,
    LC_PAPER     = 7,
    LC_NAME      = 8,
    LC_ADDRESS   = 9,

    LC_TELEPHONE      = 10,
    LC_MEASUREMENT    = 11,
    LC_IDENTIFICATION = 12
};

extern char *setlocale(int category, const char *locale);

/* FIXME: ANDROID */
/* Rather than leaving struct lconv blank, which breaks a lot of
 * existing code relying on localization, emulate the C locale
 * settings. */

#if __HACK_BUILTIN_LOCALECONV 
struct lconv {
    char* decimal_point;
    char* thousands_sep;
    char* grouping;
    char* int_curr_symbol;
    char* currency_symbol;
    char* mon_decimal_point;
    char* mon_thousands_sep;
    char* mon_grouping;
    char* positive_sign;
    char* negative_sign;
    char int_frac_digits;
    char frac_digits;
    char p_cs_precedes;
    char n_cs_precedes;
    char p_sep_by_space;
    char n_sep_by_space;
    char p_sign_posn;
    char n_sign_posn;
} __lconv_c_locale;

static inline struct lconv *localeconv(void)
{
    __lconv_c_locale.decimal_point = (char*)".";
    __lconv_c_locale.thousands_sep = (char*)"";
    __lconv_c_locale.grouping = (char*)"";
    __lconv_c_locale.int_curr_symbol = (char*)"";
    __lconv_c_locale.currency_symbol = (char*)"";
    __lconv_c_locale.mon_decimal_point = (char*)"";
    __lconv_c_locale.mon_thousands_sep = (char*)"";
    __lconv_c_locale.mon_grouping = (char*)"";
    __lconv_c_locale.positive_sign = (char*)"";
    __lconv_c_locale.negative_sign = (char*)"";
    __lconv_c_locale.int_frac_digits = CHAR_MAX;
    __lconv_c_locale.frac_digits = CHAR_MAX;
    __lconv_c_locale.p_cs_precedes = CHAR_MAX;
    __lconv_c_locale.n_cs_precedes = CHAR_MAX;
    __lconv_c_locale.p_sep_by_space = CHAR_MAX;
    __lconv_c_locale.n_sep_by_space = CHAR_MAX;
    __lconv_c_locale.p_sign_posn = CHAR_MAX;
    __lconv_c_locale.n_sign_posn = CHAR_MAX;

    /* According to documentation, the returned pointer is not to
     * be free'd by the calling program, so this is safe. */
    return &__lconv_c_locale;
}
#else
struct lconv { };
struct lconv *localeconv(void);
#endif

__END_DECLS

#endif /* _LOCALE_H_ */
