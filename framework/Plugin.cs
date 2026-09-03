// Custom Start Framework — perk-driven custom starts for Probably Stolen (MelonLoader).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using HarmonyLib;
using Il2CppInterop.Runtime;
using Il2CppInterop.Runtime.InteropTypes;
using MelonLoader;
using PsModI18n;
using MelonLoader.Utils;
using Il2Cpp;

[assembly: MelonInfo(typeof(CustomStartFramework.CustomStartFrameworkPlugin), "CustomStartFramework", "1.0.0", "Nico's Lab")]
[assembly: MelonProcess("Probably Stolen.exe")]

namespace CustomStartFramework
{
    public class CustomStartFrameworkPlugin : MelonMod
    {
        internal static int PendingStartType;
        internal static bool ItemsRemoved;
        internal static bool Injected;
        internal static bool CashGranted;
        internal static bool RentGranted;
        internal static bool UpgradesGranted;
        internal static bool ReputationGranted;

        internal static CustomStartProfile ActiveProfile;

        public override void OnInitializeMelon()
        {
            LoggerInstance.Msg($"{Info.Name} v{Info.Version} by {Info.Author} loaded.");
            LoggerInstance.Msg(CommunityInfo.QqGroupLog);

            string userData = MelonEnvironment.UserDataDirectory;
            CustomStartPerkRegistry.RegisterMany(CustomStartProfileLoader.LoadAll(userData));
            LoggerInstance.Msg(
                $"Loaded {CustomStartPerkRegistry.All.Count} custom-start profile(s) from {CustomStartProfileLoader.ResolveRoot(userData)}.");

            HarmonyInstance.PatchAll(typeof(CustomStartFrameworkPlugin).Assembly);
            LoggerInstance.Msg("Harmony patches applied.");
        }

        internal static void ProcessItems(CustomStartProfile profile, string fromHook)
        {
            if (ItemsRemoved && Injected)
            {
                MelonLogger.Msg($"  [skip] items already processed (from {fromHook}).");
                return;
            }

            List<string> removeIds = profile?.RemoveItems;
            List<LoadoutItem> addItems = profile?.Items;
            bool needRemove = removeIds != null && removeIds.Count > 0;
            bool needAdd = addItems != null && addItems.Count > 0;

            if (!needRemove && !needAdd)
            {
                ItemsRemoved = true;
                Injected = true;
                MelonLogger.Msg($"Profile '{profile?.Id}': no item add/remove configured.");
                return;
            }

            var emporium = EmporiumEntry.Instance;
            if (emporium == null || emporium.invElement == null)
            {
                MelonLogger.Msg($"Inventory not ready yet (from {fromHook}); will retry on a later hook.");
                return;
            }

            var inv = emporium.invElement;

            if (!ItemsRemoved)
            {
                if (needRemove)
                    RemoveConfiguredItems(profile.Id, inv, removeIds, fromHook);
                ItemsRemoved = true;
            }

            if (!Injected)
            {
                if (needAdd)
                    GrantItemsInternal(profile.Id, inv, addItems, fromHook);
                else
                    Injected = true;
            }
        }

        internal static void RemoveConfiguredItems(string profileId, GameGridInventory inv, List<string> removeIds, string fromHook)
        {
            MelonLogger.Msg($"Profile {profileId}: removing up to {removeIds.Count} item(s) via {fromHook} (before add).");
            foreach (string rawId in removeIds)
            {
                string id = rawId?.Trim();
                if (string.IsNullOrEmpty(id)) continue;

                GameItem target = null;
                try
                {
                    var children = inv.childItems;
                    if (children == null) continue;
                    for (int i = 0; i < children.Count; i++)
                    {
                        GameItem item = children[i];
                        if (item == null) continue;
                        string ident = null;
                        try { ident = item.identifier; } catch { }
                        if (string.Equals(ident, id, StringComparison.Ordinal))
                        {
                            target = item;
                            break;
                        }
                    }
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to scan inventory for '{id}': {e.Message}");
                    continue;
                }

                if (target == null)
                {
                    MelonLogger.Msg($"  Remove skip (not on counter): {id}");
                    continue;
                }

                try
                {
                    bool ok = inv.Expel(target);
                    MelonLogger.Msg($"  Removed item: {id} (expel={ok})");
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to remove '{id}': {e.Message}");
                }
            }
        }

        internal static void GrantItemsInternal(string profileId, GameGridInventory inv, List<LoadoutItem> items, string fromHook)
        {
            MelonLogger.Msg($"Profile {profileId}: granting {items.Count} start item(s) via {fromHook}.");
            foreach (LoadoutItem spec in items)
            {
                string rawId = spec?.Id;
                try
                {
                    if (spec == null || string.IsNullOrWhiteSpace(spec.Id)) continue;
                    string id = spec.Id.Trim();
                    GameItem item = DirectoryMaster.Item(id, true);
                    if (item == null)
                    {
                        MelonLogger.Warning($"Item not found: {id}");
                        continue;
                    }
                    string realId = null;
                    try { realId = item.identifier; } catch { }
                    if (string.IsNullOrEmpty(realId))
                    {
                        MelonLogger.Warning($"Item '{id}' resolved to an EMPTY item (identifier empty); skipping.");
                        continue;
                    }
                    ApplyItemModifiers(item, spec);
                    SlotMarker slot = null;
                    try
                    {
                        slot = inv.TryFindOneValidInventorySlot(item, false);
                    }
                    catch (Exception e) { MelonLogger.Warning($"TryFindOneValidInventorySlot threw: {e.Message}"); }
                    if (slot == null)
                    {
                        MelonLogger.Warning($"No free slot for {id}; falling back to UncheckedAcceptAll.");
                        var list = new Il2CppSystem.Collections.Generic.List<GameItem>();
                        list.Add(item);
                        inv.UncheckedAcceptAll(list);
                    }
                    else
                    {
                        int idx = -1;
                        try { idx = slot.index; } catch { }
                        int accepted = -1;
                        try { accepted = slot.AcceptUnchecked(); }
                        catch (Exception e) { MelonLogger.Warning($"AcceptUnchecked threw: {e.Message}"); }
                        MelonLogger.Msg($"Granted item: {id} (identifier='{realId}') slotIndex={idx} accepted={accepted}");
                    }
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to grant '{rawId}': {e}");
                }
            }
            Injected = true;
        }

        static void ApplyItemModifiers(GameItem item, LoadoutItem spec)
        {
            if (spec.Charge.HasValue)
                ApplyCharge(item, spec);
            if (!string.IsNullOrWhiteSpace(spec.Water) || spec.VolumeMl.HasValue)
                ApplyWater(item, spec);
        }

        static void ApplyCharge(GameItem item, LoadoutItem spec)
        {
            int charge = spec.Charge.Value;
            if (charge < 0)
            {
                MelonLogger.Warning($"Charge {charge} on '{spec.Id}' is negative; clamping to 0.");
                charge = 0;
            }
            try
            {
                PowerHelper.SetPowerSourceAt(item, charge);
                try { PowerHelper.UpdateEnergyCreditSprite(item); } catch { }
                MelonLogger.Msg($"  charge={charge} on {spec.Id}");
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"Failed to set charge on '{spec.Id}': {e.Message}");
            }
        }

        static void ApplyWater(GameItem item, LoadoutItem spec)
        {
            if (string.IsNullOrWhiteSpace(spec.Water))
            {
                MelonLogger.Warning($"Item '{spec.Id}' has volumeMl but no water type; skipping fill.");
                return;
            }
            if (!WaterTypeParser.TryParse(spec.Water, out WaterKind kind))
            {
                MelonLogger.Warning($"Unknown water type '{spec.Water}' on '{spec.Id}'.");
                return;
            }
            try
            {
                WaterHelper.EmptyContainer(item);
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"EmptyContainer failed on '{spec.Id}': {e.Message}");
                return;
            }
            if (spec.VolumeMl == 0)
            {
                MelonLogger.Msg($"  water emptied on {spec.Id}");
                return;
            }
            int cap = -1;
            try { cap = WaterHelper.GetFreeCapacity(item); } catch { }
            bool fillFull = spec.VolumeMl == null;
            int configMl = fillFull ? 0 : spec.VolumeMl.Value;
            int amount = fillFull ? -1 : checked(configMl * 1000);
            if (!fillFull && configMl < 0)
            {
                MelonLogger.Warning($"volumeMl {configMl} on '{spec.Id}' is negative; treating as empty.");
                return;
            }
            if (!fillFull && cap > 0 && amount > cap)
            {
                MelonLogger.Warning($"volumeMl {configMl} exceeds capacity on '{spec.Id}'; clamping.");
                amount = cap;
                fillFull = true;
            }
            try
            {
                FillWater(item, kind, fillFull, fillFull ? cap : amount);
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"Failed to fill '{spec.Id}' with {kind}: {e.Message}");
                return;
            }
            try { WaterFeatureHelper.InitWaterFeature(item, true); } catch { }
        }

        static void FillWater(GameItem item, WaterKind kind, bool fillFull, int amount)
        {
            switch (kind)
            {
                case WaterKind.Pure:
                    if (amount <= 0)
                        throw new InvalidOperationException("pure water fill requires a known container capacity.");
                    WaterHelper.AddPureWater(item, amount);
                    break;
                case WaterKind.HighQuality:
                    if (fillFull) WaterHelper.FillWithHighQualityWater(item);
                    else WaterHelper.AddHighQualityWater(item, amount);
                    break;
                case WaterKind.Base:
                    if (fillFull) WaterHelper.FillWithBaseWater(item);
                    else WaterHelper.AddBaseWater(item, amount);
                    break;
                case WaterKind.Ghost:
                    if (fillFull) WaterHelper.FillWithGhostwater(item);
                    else WaterHelper.AddGhostWater(item, amount);
                    break;
                case WaterKind.Rust:
                    if (fillFull) WaterHelper.FillWithRustWaterLowEnd(item);
                    else WaterHelper.AddRustWater(item, amount);
                    break;
                case WaterKind.Gutterflow:
                    if (amount <= 0)
                        throw new InvalidOperationException("gutterflow fill requires a known container capacity.");
                    WaterHelper.AddGutterflow(item, amount);
                    break;
                case WaterKind.Nutrient:
                    throw new InvalidOperationException("nutrient solution is not available in this game build.");
            }
        }

        internal static void GrantCash(PlayerStore store, CustomStartProfile profile)
        {
            if (CashGranted) return;
            int amount = profile?.ExtraCash ?? 0;
            if (amount == 0)
            {
                CashGranted = true;
                return;
            }
            if (store == null)
            {
                try { store = PlayerStore.Instance; } catch { }
            }
            if (store == null)
            {
                MelonLogger.Msg("Extra cash not granted yet: PlayerStore not available; will retry.");
                return;
            }
            try
            {
                store.playerCash += amount;
                MelonLogger.Msg($"Profile {profile.Id}: adjusted cash by {amount} (playerCash={store.playerCash}).");
                CashGranted = true;
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"Failed to grant extra cash: {e}");
                CashGranted = true;
            }
        }

        internal static void GrantRent(PlayerStore store, CustomStartProfile profile)
        {
            if (RentGranted) return;
            int amount = profile?.ExtraRent ?? 0;
            if (amount == 0)
            {
                RentGranted = true;
                return;
            }
            if (store == null)
            {
                try { store = PlayerStore.Instance; } catch { }
            }
            if (store == null)
            {
                MelonLogger.Msg("Extra rent not granted yet: PlayerStore not available; will retry.");
                return;
            }
            try
            {
                store.startingRent += amount;
                store.rentValue += amount;
                if (store.startingRent < 0) store.startingRent = 0;
                if (store.rentValue < 0) store.rentValue = 0;
                MelonLogger.Msg($"Profile {profile.Id}: adjusted rent by {amount}.");
                RentGranted = true;
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"Failed to grant extra rent: {e}");
                RentGranted = true;
            }
        }

        internal static void GrantUpgrades(CustomStartProfile profile)
        {
            if (UpgradesGranted) return;
            List<string> ids = profile?.UnlockedUpgrades;
            if (ids == null || ids.Count == 0)
            {
                UpgradesGranted = true;
                return;
            }
            MelonLogger.Msg($"Profile {profile.Id}: granting {ids.Count} unlocked wilds network upgrade(s).");
            foreach (string id in ids)
            {
                if (string.IsNullOrWhiteSpace(id)) continue;
                try
                {
                    NetworkUpgrade upgrade = NetworkUpgrade.GetUpgradeById(id.Trim());
                    if (upgrade == null)
                    {
                        MelonLogger.Warning($"Upgrade not found: {id}");
                        continue;
                    }
                    if (upgrade.IsUnlocked())
                    {
                        MelonLogger.Msg($"  Upgrade already unlocked: {id}");
                        continue;
                    }
                    upgrade.Unlock();
                    MelonLogger.Msg($"  Granted upgrade: {id}");
                }
                catch (Exception e)
                {
                    MelonLogger.Warning($"Failed to grant upgrade '{id}': {e}");
                }
            }
            UpgradesGranted = true;
        }

        internal static void GrantFactionReputation(CustomStartProfile profile)
        {
            if (ReputationGranted) return;
            Dictionary<string, int> deltas = profile?.FactionReputationDelta;
            if (deltas == null || deltas.Count == 0)
            {
                ReputationGranted = true;
                return;
            }
            bool any = false;
            foreach (int v in deltas.Values)
            {
                if (v != 0) { any = true; break; }
            }
            if (!any)
            {
                ReputationGranted = true;
                return;
            }
            MelonLogger.Msg($"Profile {profile.Id}: applying faction reputation delta(s).");
            FactionReputationHelper.ApplyDeltas(deltas);
            ReputationGranted = true;
        }

        internal static void TryInject(PlayerStore store, string hook)
        {
            MelonLogger.Msg($"[diag] {hook} called (PendingStartType={PendingStartType})");
            if (PendingStartType <= 0) return;

            CustomStartProfile resolved = null;
            if (ActiveProfile == null &&
                !CustomStartPerkRegistry.TryResolveActiveProfile(PendingStartType, out resolved))
            {
                MelonLogger.Msg($"No active custom-start perk for startType={PendingStartType}; skipping injection.");
                PendingStartType = 0;
                return;
            }

            if (ActiveProfile == null)
                ActiveProfile = resolved;

            GrantCash(store, ActiveProfile);
            GrantRent(store, ActiveProfile);
            GrantUpgrades(ActiveProfile);
            GrantFactionReputation(ActiveProfile);
            ProcessItems(ActiveProfile, hook);
            if (ItemsRemoved && Injected)
            {
                PendingStartType = 0;
                ActiveProfile = null;
            }
        }
    }

    [HarmonyPatch(typeof(PlayerStore), "InitialSave")]
    public static class InitialSavePatch
    {
        private static int _startTypeFieldOffset = -1;

        private static int ResolveStartTypeFieldOffset()
        {
            if (_startTypeFieldOffset >= 0) return _startTypeFieldOffset;
            try
            {
                IntPtr klass = Il2CppClassPointerStore.GetNativeClassPointer(typeof(PlayerStore));
                IntPtr field = IL2CPP.il2cpp_class_get_field_from_name(klass, "startType");
                if (field == IntPtr.Zero)
                {
                    MelonLogger.Error("Failed to resolve PlayerStore.startType: field not found.");
                    return -1;
                }
                int off = (int)IL2CPP.il2cpp_field_get_offset(field);
                _startTypeFieldOffset = off;
                MelonLogger.Msg($"Resolved PlayerStore.startType field offset = 0x{off:X} ({off}).");
            }
            catch (Exception e)
            {
                MelonLogger.Error($"Failed to resolve PlayerStore.startType field offset: {e}");
            }
            return _startTypeFieldOffset;
        }

        static void Postfix(PlayerStore __instance)
        {
            try
            {
                if (__instance == null) return;
                int offset = ResolveStartTypeFieldOffset();
                if (offset < 0) return;
                var baseObj = (Il2CppObjectBase)(object)__instance;
                int startType = Marshal.ReadInt32(baseObj.Pointer + offset);
                MelonLogger.Msg($"[diag] InitialSave called, startType={startType}");
                if (startType <= 0) return;
                CustomStartFrameworkPlugin.PendingStartType = startType;
                CustomStartFrameworkPlugin.ActiveProfile = null;
                CustomStartFrameworkPlugin.ItemsRemoved = false;
                CustomStartFrameworkPlugin.Injected = false;
                CustomStartFrameworkPlugin.CashGranted = false;
                CustomStartFrameworkPlugin.RentGranted = false;
                CustomStartFrameworkPlugin.UpgradesGranted = false;
                CustomStartFrameworkPlugin.ReputationGranted = false;
            }
            catch (Exception e)
            {
                MelonLogger.Error($"InitialSave postfix error: {e}");
            }
        }
    }

    [HarmonyPatch]
    public static class PlayerStoreInjectionHooks
    {
        static IEnumerable<MethodBase> TargetMethods()
        {
            return new[]
            {
                "BeginDay",
                "OpenShutter",
                "OnLateShutterOpen",
                "GetNextClient",
                "OnShutterOpened"
            }.Select(name => AccessTools.Method(typeof(PlayerStore), name));
        }

        static void Postfix(PlayerStore __instance, MethodBase __originalMethod)
        {
            string hook = __originalMethod?.Name ?? "unknown";
            try { CustomStartFrameworkPlugin.TryInject(__instance, hook); }
            catch (Exception e) { MelonLogger.Error($"{hook} postfix error: {e}"); }
        }
    }

    [HarmonyPatch(typeof(EmporiumEntry), "Start")]
    public static class EmporiumStartPatch
    {
        static void Postfix()
        {
            try
            {
                if (CustomStartFrameworkPlugin.PendingStartType <= 0) return;
                PlayerStore store = null;
                try { store = PlayerStore.Instance; } catch { }
                CustomStartFrameworkPlugin.TryInject(store, "EmporiumStart");
            }
            catch (Exception e) { MelonLogger.Error($"EmporiumStart postfix error: {e}"); }
        }
    }
}
