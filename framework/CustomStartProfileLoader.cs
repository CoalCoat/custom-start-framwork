using System;
using System.Collections.Generic;
using System.IO;
using MelonLoader;

namespace CustomStartFramework
{
    public static class CustomStartProfileLoader
    {
        public const string RootFolderName = "custom-start";

        public static string ResolveRoot(string userDataDirectory) =>
            Path.Combine(userDataDirectory, RootFolderName);

        public static List<CustomStartProfile> LoadAll(string userDataDirectory)
        {
            string root = ResolveRoot(userDataDirectory);
            Directory.CreateDirectory(root);

            var profiles = new List<CustomStartProfile>();
            foreach (string folder in Directory.EnumerateDirectories(root))
            {
                string profilePath = Path.Combine(folder, CustomStartProfile.ProfileFileName);
                if (!File.Exists(profilePath))
                    continue;
                try
                {
                    CustomStartProfile profile = CustomStartProfile.LoadFromFolder(folder);
                    profiles.Add(profile);
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to load custom start profile in '{folder}': {e.Message}");
                }
            }
            profiles.Sort((a, b) => string.Compare(a.Id, b.Id, StringComparison.OrdinalIgnoreCase));
            return profiles;
        }

        public static void EnsureExampleProfile(string userDataDirectory, CustomStartProfile template)
        {
            if (template == null || string.IsNullOrWhiteSpace(template.Id))
                return;
            string folder = Path.Combine(ResolveRoot(userDataDirectory), template.Id);
            string profilePath = Path.Combine(folder, CustomStartProfile.ProfileFileName);
            if (File.Exists(profilePath))
                return;
            template.SaveToFolder(folder);
            MelonLogger.Msg($"Created example custom start profile at {profilePath}");
        }
    }
}
