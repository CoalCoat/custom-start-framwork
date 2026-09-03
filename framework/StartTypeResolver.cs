using Il2Cpp;

namespace CustomStartFramework
{
    internal static class StartTypeResolver
    {
        internal static int Resolve()
        {
            int fromData = TryFromNewGameData();
            if (fromData > 0)
                return Cache(fromData);

            if (CustomStartFrameworkPlugin.PendingStartType > 0)
                return CustomStartFrameworkPlugin.PendingStartType;

            return 0;
        }

        internal static bool IsVisibleForStartType(CustomStartProfile profile, int startType)
        {
            if (profile == null)
                return false;
            if (startType <= 0)
                return profile.AllowedStartTypes == null || profile.AllowedStartTypes.Count == 0;
            return profile.AllowsStartType(startType);
        }

        private static int TryFromNewGameData()
        {
            try
            {
                NewGameData data = NewGameData.Instance;
                if (data != null)
                    return (int)data.startType;
            }
            catch
            {
                // ignored
            }
            return 0;
        }

        private static int Cache(int startType)
        {
            CustomStartFrameworkPlugin.PendingStartType = startType;
            return startType;
        }
    }
}
