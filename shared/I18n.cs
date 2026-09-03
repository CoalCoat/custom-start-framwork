namespace PsModI18n
{
    internal static class I18n
    {
        public static string T(string zh, string en)
        {
#if MOD_LANG_EN
            return en;
#else
            return zh;
#endif
        }

        public static string F(string zhFormat, string enFormat, params object[] args) =>
            string.Format(T(zhFormat, enFormat), args);
    }
}
