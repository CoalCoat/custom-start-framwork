using System;
using System.Collections.Generic;
using System.IO;
using Il2Cpp;
using Il2CppInterop.Runtime.InteropTypes.Arrays;
using MelonLoader;
using UnityEngine;

namespace CustomStartFramework
{
    internal static class PerkIconLoader
    {
        private static readonly Dictionary<string, Sprite> Cache =
            new Dictionary<string, Sprite>(StringComparer.Ordinal);

        internal static Sprite Get(CustomStartProfile profile)
        {
            if (profile == null || string.IsNullOrEmpty(profile.Id))
                return null;
            if (Cache.TryGetValue(profile.Id, out Sprite cached))
                return cached;

            Sprite sprite = LoadFromFile(profile.ResolveIconPath())
                ?? LoadFromEmbedded(profile.Id);
            if (sprite != null)
                Cache[profile.Id] = sprite;
            return sprite;
        }

        internal static void InjectAll()
        {
            var perkIcons = StartingPerkIconLoader.perkIcons;
            if (perkIcons == null)
            {
                MelonLogger.Warning("Perk icon dictionary was not initialized.");
                return;
            }

            int count = 0;
            foreach (CustomStartProfile profile in CustomStartPerkRegistry.All)
            {
                Sprite sprite = Get(profile);
                if (sprite == null)
                    continue;
                perkIcons[profile.Id] = sprite;
                count++;
            }
            MelonLogger.Msg($"Custom-start perk icons injected: {count}/{CustomStartPerkRegistry.All.Count}.");
        }

        private static Sprite LoadFromFile(string path)
        {
            if (string.IsNullOrEmpty(path) || !File.Exists(path))
                return null;
            try
            {
                byte[] bytes = File.ReadAllBytes(path);
                return CreateSprite(bytes);
            }
            catch (Exception e)
            {
                MelonLogger.Warning($"Failed to load perk icon '{path}': {e.Message}");
                return null;
            }
        }

        private static Sprite LoadFromEmbedded(string perkId)
        {
            string resourceName = $"CustomStartFramework.Icons.{perkId}.png";
            try
            {
                using Stream stream = typeof(CustomStartFrameworkPlugin).Assembly.GetManifestResourceStream(resourceName);
                if (stream == null)
                    return null;
                byte[] bytes = new byte[stream.Length];
                if (stream.Read(bytes, 0, bytes.Length) != bytes.Length)
                    return null;
                return CreateSprite(bytes);
            }
            catch
            {
                return null;
            }
        }

        private static Sprite CreateSprite(byte[] bytes)
        {
            Texture2D texture = new Texture2D(2, 2, TextureFormat.RGBA32, false, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp,
                hideFlags = HideFlags.HideAndDontSave
            };
            if (!ImageConversion.LoadImage(texture, new Il2CppStructArray<byte>(bytes), false))
            {
                UnityEngine.Object.Destroy(texture);
                return null;
            }
            Sprite sprite = Sprite.Create(
                texture,
                new Rect(0f, 0f, texture.width, texture.height),
                new Vector2(0.5f, 0.5f),
                100f);
            sprite.hideFlags = HideFlags.HideAndDontSave;
            return sprite;
        }
    }
}
