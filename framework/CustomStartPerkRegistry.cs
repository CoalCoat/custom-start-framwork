using System;
using System.Collections.Generic;
using Il2Cpp;
using MelonLoader;

namespace CustomStartFramework
{
    public static class CustomStartPerkRegistry
    {
        private static readonly Dictionary<string, CustomStartProfile> ProfilesById =
            new Dictionary<string, CustomStartProfile>(StringComparer.Ordinal);

        public static IReadOnlyCollection<CustomStartProfile> All => ProfilesById.Values;

        public static void Clear() => ProfilesById.Clear();

        public static void Register(CustomStartProfile profile)
        {
            if (profile == null || string.IsNullOrWhiteSpace(profile.Id))
                throw new ArgumentException("profile.id is required", nameof(profile));
            ProfilesById[profile.Id] = profile;
        }

        public static void RegisterMany(IEnumerable<CustomStartProfile> profiles)
        {
            if (profiles == null)
                return;
            foreach (CustomStartProfile profile in profiles)
                Register(profile);
        }

        public static CustomStartProfile Find(string id)
        {
            if (string.IsNullOrEmpty(id))
                return null;
            ProfilesById.TryGetValue(id, out CustomStartProfile profile);
            return profile;
        }

        public static bool IsActive(string id)
        {
            try
            {
                return StartingPerk.IsPerkActive(id);
            }
            catch
            {
                return false;
            }
        }

        public static bool TryResolveActiveProfile(int playerStartType, out CustomStartProfile profile)
        {
            profile = null;
            CustomStartProfile firstMatch = null;
            int matchCount = 0;

            foreach (CustomStartProfile candidate in ProfilesById.Values)
            {
                if (!candidate.AllowsStartType(playerStartType))
                    continue;
                if (!IsActive(candidate.Id))
                    continue;
                firstMatch = candidate;
                matchCount++;
            }

            if (matchCount == 0)
                return false;

            if (matchCount > 1)
                MelonLogger.Warning(
                    $"Multiple custom-start perks active for startType={playerStartType}; using '{firstMatch.Id}'.");

            profile = firstMatch;
            return true;
        }

        public static IEnumerable<CustomStartProfile> GetVisibleForStartType(int startType)
        {
            foreach (CustomStartProfile profile in ProfilesById.Values)
            {
                if (profile.AllowsStartType(startType))
                    yield return profile;
            }
        }
    }
}
