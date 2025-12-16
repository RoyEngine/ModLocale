package dal.impl.campaign.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsGunneryImplants {
	
	public static boolean loadStock = false;
	public static float RECOIL_BONUS = 35f;
	public static float TARGET_LEADING_BONUS = 100f;
	public static float RANGE_BONUS = 10f;
	public static float WEAPON_HP_BONUS = 20f;
	public static float GEN_SKILL_MULT = 0.5f;
	
	public static boolean isOfficer(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null) return false;
		return !member.getCaptain().isDefault();
	}

	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getMaxRecoilMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
			stats.getRecoilPerShotMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
			// slower recoil recovery, also, to match the reduced recoil-per-shot
			// overall effect is same as without skill but halved in every respect
			stats.getRecoilDecayMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMaxRecoilMult().unmodify(id);
			stats.getRecoilPerShotMult().unmodify(id);
			stats.getRecoilDecayMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(RECOIL_BONUS) + "% 武器后坐力";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level1B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getMaxRecoilMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
			stats.getRecoilPerShotMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
			// slower recoil recovery, also, to match the reduced recoil-per-shot
			// overall effect is same as without skill but halved in every respect
			stats.getRecoilDecayMult().modifyMult(id, 1f - (0.01f * RECOIL_BONUS));
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMaxRecoilMult().unmodify(id);
			stats.getRecoilPerShotMult().unmodify(id);
			stats.getRecoilDecayMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(RECOIL_BONUS * GEN_SKILL_MULT) + "% 武器后坐力";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}

	public static class Level2 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getAutofireAimAccuracy().modifyFlat(id, TARGET_LEADING_BONUS * 0.01f);
			//stats.getCargoMod().modifyFlat(id, 100 * level);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getAutofireAimAccuracy().unmodify(id);
			//stats.getCargoMod().unmodify();
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(TARGET_LEADING_BONUS) + "% 自动开火武器精度";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level2B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getAutofireAimAccuracy().modifyFlat(id, TARGET_LEADING_BONUS * 0.01f * 0.5f);
			//stats.getCargoMod().modifyFlat(id, 100 * level);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getAutofireAimAccuracy().unmodify(id);
			//stats.getCargoMod().unmodify();
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(TARGET_LEADING_BONUS * GEN_SKILL_MULT) + "% 自动开火武器精度";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level3 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getBallisticWeaponRangeBonus().modifyPercent(id, RANGE_BONUS);
			stats.getEnergyWeaponRangeBonus().modifyPercent(id, RANGE_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getBallisticWeaponRangeBonus().unmodify(id);
			stats.getEnergyWeaponRangeBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(RANGE_BONUS) + "% 实弹与能量武器射程";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	public static class Level3B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getBallisticWeaponRangeBonus().modifyPercent(id, RANGE_BONUS/2f);
			stats.getEnergyWeaponRangeBonus().modifyPercent(id, RANGE_BONUS/2f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getBallisticWeaponRangeBonus().unmodify(id);
			stats.getEnergyWeaponRangeBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(RANGE_BONUS * GEN_SKILL_MULT) + "% 实弹与能量武器射程";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level4 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getWeaponHealthBonus().modifyPercent(id, WEAPON_HP_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getWeaponHealthBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(WEAPON_HP_BONUS) + "% 武器在失效前所能承受的伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}	
}
