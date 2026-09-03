using System;
using System.Collections.Generic;
using Il2Cpp;
using MelonLoader;

namespace CustomStartFramework
{
    internal static class FactionReputationHelper
    {
        sealed class FactionRepBinding
        {
            internal Action<int> Mod;
            internal string LogName;
        }

        static readonly Dictionary<string, FactionRepBinding> Bindings =
            new Dictionary<string, FactionRepBinding>(StringComparer.OrdinalIgnoreCase)
            {
                ["lower"] = Bind(StoreReputation.ModLLReputation, "Lower Levels"),
                ["ll"] = Bind(StoreReputation.ModLLReputation, "Lower Levels"),
                ["lower_levels"] = Bind(StoreReputation.ModLLReputation, "Lower Levels"),
                ["faction_lower_level"] = Bind(StoreReputation.ModLLReputation, "Lower Levels"),

                ["upper"] = Bind(StoreReputation.ModULReputation, "Upper Levels"),
                ["ul"] = Bind(StoreReputation.ModULReputation, "Upper Levels"),
                ["upper_levels"] = Bind(StoreReputation.ModULReputation, "Upper Levels"),
                ["faction_upper_level"] = Bind(StoreReputation.ModULReputation, "Upper Levels"),

                ["security"] = Bind(StoreReputation.ModSecReputation, "Security"),
                ["sec"] = Bind(StoreReputation.ModSecReputation, "Security"),
                ["faction_security"] = Bind(StoreReputation.ModSecReputation, "Security"),

                ["black_market"] = Bind(StoreReputation.ModBMReputation, "Black Market"),
                ["bm"] = Bind(StoreReputation.ModBMReputation, "Black Market"),
                ["crime"] = Bind(StoreReputation.ModBMReputation, "Black Market"),
                ["faction_black_market"] = Bind(StoreReputation.ModBMReputation, "Black Market"),

                ["revolution"] = Bind(StoreReputation.ModRevReputation, "Revolution"),
                ["rev"] = Bind(StoreReputation.ModRevReputation, "Revolution"),
                ["faction_revolution"] = Bind(StoreReputation.ModRevReputation, "Revolution"),

                ["cartel"] = Bind(StoreReputation.ModCartelReputation, "Cartel"),
                ["faction_cartel"] = Bind(StoreReputation.ModCartelReputation, "Cartel"),
            };

        static FactionRepBinding Bind(Action<int> mod, string logName) =>
            new FactionRepBinding { Mod = mod, LogName = logName };

        internal static void ApplyDeltas(Dictionary<string, int> deltas)
        {
            if (deltas == null || deltas.Count == 0) return;

            foreach (KeyValuePair<string, int> entry in deltas)
            {
                string key = entry.Key?.Trim();
                if (string.IsNullOrEmpty(key)) continue;
                if (entry.Value == 0) continue;

                if (!Bindings.TryGetValue(key, out FactionRepBinding binding))
                {
                    MelonLogger.Warning($"Unknown faction reputation key '{key}'. Use lower/upper/security/black_market/revolution/cartel or FACTION_* id aliases.");
                    continue;
                }

                try
                {
                    binding.Mod(entry.Value);
                    MelonLogger.Msg($"  {binding.LogName}: delta {entry.Value}.");
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to apply {binding.LogName} reputation delta {entry.Value}: {e.Message}");
                }
            }
        }
    }
}
