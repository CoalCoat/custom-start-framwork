namespace PsModI18n
{
    internal static class I18n
    {
        public static string T(string zh, string en)
        {
            if (GameLocaleHelper.PreferEnglish())
            {
                if (!string.IsNullOrWhiteSpace(en))
                    return en;
                return zh ?? "";
            }

            return string.IsNullOrWhiteSpace(zh) ? en ?? "" : zh;
        }

        public static string F(string zhFormat, string enFormat, params object[] args) =>
            string.Format(T(zhFormat, enFormat), args);
    }
}
