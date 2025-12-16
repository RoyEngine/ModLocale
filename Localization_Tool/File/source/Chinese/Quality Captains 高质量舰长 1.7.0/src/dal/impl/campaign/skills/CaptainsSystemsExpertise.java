package dal.impl.campaign.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class CaptainsSystemsExpertise {
	
	public static float PEAK_TIME_BONUS = 30f;
	
	public static float CHARGES_PERCENT = 35f; //100f
	public static float REGEN_PERCENT = 25f; //50f
	public static float SYSTEM_COOLDOWN_REDUCTION_PERCENT = 25f; //33f
	public static float RANGE_PERCENT = 25f; //50
	public static int CHARGES_BONUS = 1;
	
	public static float NO_OFFICER_FACTOR = 0.5f;
	

	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			//stats.getSystemUsesBonus().modifyPercent(id, CHARGES_PERCENT);
			stats.getSystemUsesBonus().modifyFlat(id, 1);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemUsesBonus().unmodifyPercent(id);
		}
		
		public String getEffectDescription(float level) {
			//return "If the ship's system has charges: +" + (int)(CHARGES_PERCENT) + "% charges";
			return "若舰船系统存在充能数: +" + CHARGES_BONUS + " 充能数量";
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
			stats.getSystemRegenBonus().modifyPercent(id, REGEN_PERCENT);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemRegenBonus().unmodifyPercent(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统能回复充能: +" + (int)(REGEN_PERCENT) + "% 回充速率";
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
			stats.getSystemRegenBonus().modifyPercent(id, REGEN_PERCENT*NO_OFFICER_FACTOR);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemRegenBonus().unmodifyPercent(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统能回复充能: +" + (int)(REGEN_PERCENT*NO_OFFICER_FACTOR) + "% 回充速率";
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
			stats.getSystemRangeBonus().modifyPercent(id, RANGE_PERCENT);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemRangeBonus().unmodifyPercent(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统有释放距离: +" + (int)(RANGE_PERCENT) + "% 释放距离";
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
			stats.getSystemRangeBonus().modifyPercent(id, RANGE_PERCENT*NO_OFFICER_FACTOR);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemRangeBonus().unmodifyPercent(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统有释放距离: +" + (int)(RANGE_PERCENT*NO_OFFICER_FACTOR) + "% 释放距离";
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
			stats.getSystemCooldownBonus().modifyMult(id, 1f - SYSTEM_COOLDOWN_REDUCTION_PERCENT / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemCooldownBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统有冷却时间: -" + (int)(SYSTEM_COOLDOWN_REDUCTION_PERCENT) + "% 冷却时间";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}

	public static class Level4B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getSystemCooldownBonus().modifyMult(id, 1f - (SYSTEM_COOLDOWN_REDUCTION_PERCENT*NO_OFFICER_FACTOR) / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSystemCooldownBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "若舰船系统有冷却时间: -" + (int)(SYSTEM_COOLDOWN_REDUCTION_PERCENT*NO_OFFICER_FACTOR) + "% 冷却时间";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}

	
	public static class Level5 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getPeakCRDuration().modifyFlat(id, PEAK_TIME_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getPeakCRDuration().unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(PEAK_TIME_BONUS) + " 秒峰值时间\n";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	
}
