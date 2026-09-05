using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using PsModI18n;

namespace CustomStartFramework
{
    public sealed class LocalizedText
    {
        public string Zh { get; set; }
        public string En { get; set; }

        public string Pick() => I18n.T(Zh, En);
    }

    /// <summary>
    /// One custom-start profile stored as UserData/custom-start/{folder}/profile.json.
    /// </summary>
    public sealed class CustomStartProfile
    {
        public const int CurrentVersion = 1;
        public const string ProfileFileName = "profile.json";
        public const string IconFileName = "icon.png";

        public int Version { get; set; } = CurrentVersion;
        public string Id { get; set; }
        public LocalizedText Name { get; set; } = new LocalizedText();
        public LocalizedText Description { get; set; } = new LocalizedText();
        public int Cost { get; set; } = 0;
        public int Type { get; set; } = 0;
        public List<int> AllowedStartTypes { get; set; } = new List<int>();

        public List<LoadoutItem> Items { get; set; } = new List<LoadoutItem>();
        public List<string> RemoveItems { get; set; } = new List<string>();
        public int ExtraCash { get; set; }
        public int ExtraRent { get; set; }

        /// <summary>Added to PlayerStore.retailMarkup after start-type baseline is applied. Not an absolute percent.</summary>
        public int RetailMarkupDelta { get; set; }

        /// <summary>Added to contrabandMarkupLow/Mid/High/Critial. Int JSON applies uniform delta to all tiers.</summary>
        public ContrabandMarkupDelta ContrabandMarkupDelta { get; set; }

        /// <summary>Added to PlayerStore.baseStoreAttractiveness (typical baseline ~250). Clamped to &gt;= 0 after apply.</summary>
        public int BaseStoreAttractivenessDelta { get; set; }

        public List<string> UnlockedUpgrades { get; set; } = new List<string>();
        public Dictionary<string, int> FactionReputationDelta { get; set; } =
            FactionDefaults.CreateReputationDelta();

        /// <summary>
        /// When true (default), lower-levels rep deltas from this profile do not change Wild Favor.
        /// The game otherwise syncs Wild Favor from Lower Levels reputation on rep updates.
        /// </summary>
        public bool CompensateWildFavorForLowerRep { get; set; } = true;

        [JsonIgnore]
        public string FolderPath { get; set; }

        [JsonIgnore]
        public string FolderName =>
            string.IsNullOrEmpty(FolderPath) ? Id : Path.GetFileName(FolderPath);

        internal static readonly JsonSerializerOptions JsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            ReadCommentHandling = JsonCommentHandling.Skip,
            AllowTrailingCommas = true,
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            Converters = { new LoadoutItemConverter() }
        };

        public bool AllowsStartType(int startType)
        {
            if (AllowedStartTypes == null || AllowedStartTypes.Count == 0)
                return true;
            for (int i = 0; i < AllowedStartTypes.Count; i++)
            {
                if (AllowedStartTypes[i] == startType)
                    return true;
            }
            return false;
        }

        public static CustomStartProfile FromJson(string json)
        {
            CustomStartProfile profile = JsonSerializer.Deserialize<CustomStartProfile>(json, JsonOptions);
            if (profile == null)
                throw new InvalidDataException("profile parsed to null");
            if (string.IsNullOrWhiteSpace(profile.Id))
                throw new InvalidDataException("profile.id is required");
            profile.Id = profile.Id.Trim();
            if (profile.FactionReputationDelta == null || profile.FactionReputationDelta.Count == 0)
                profile.FactionReputationDelta = FactionDefaults.CreateReputationDelta();
            return profile;
        }

        public string ToJson() => JsonSerializer.Serialize(this, JsonOptions);

        public static CustomStartProfile LoadFromFolder(string folderPath)
        {
            string path = Path.Combine(folderPath, ProfileFileName);
            if (!File.Exists(path))
                throw new FileNotFoundException("profile.json not found", path);
            CustomStartProfile profile = FromJson(File.ReadAllText(path));
            profile.FolderPath = folderPath;
            return profile;
        }

        public void SaveToFolder(string folderPath)
        {
            Directory.CreateDirectory(folderPath);
            FolderPath = folderPath;
            File.WriteAllText(Path.Combine(folderPath, ProfileFileName), ToJson());
        }

        public string ResolveIconPath()
        {
            if (string.IsNullOrEmpty(FolderPath))
                return null;
            string path = Path.Combine(FolderPath, IconFileName);
            return File.Exists(path) ? path : null;
        }
    }
}
