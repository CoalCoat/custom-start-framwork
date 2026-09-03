using System;
using UnityEngine.Localization;
using UnityEngine.Localization.Settings;

namespace CustomStartFramework
{
    internal static class GameLocaleHelper
    {
        internal static bool PreferEnglish()
        {
            try
            {
                Locale locale = LocalizationSettings.SelectedLocale;
                if (locale == null)
                    return false;

                string code = locale.Identifier.Code;
                if (string.IsNullOrWhiteSpace(code))
                    return false;

                code = code.Trim().ToLowerInvariant();
                return code.StartsWith("en", StringComparison.Ordinal);
            }
            catch
            {
#if MOD_LANG_EN
                return true;
#else
                return false;
#endif
            }
        }
    }
}
