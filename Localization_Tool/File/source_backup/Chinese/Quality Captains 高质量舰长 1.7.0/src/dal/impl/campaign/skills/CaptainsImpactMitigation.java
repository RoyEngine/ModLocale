package dal.impl.campaign.skills;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class CaptainsImpactMitigation {
	
	public static boolean loadStock = false;
	public static float ARMOR_BONUS = 150;
	public static float MAX_DAMAGE_REDUCTION_BONUS = 0.05f;
	public static float MIN_ARMOR_FRACTION_BONUS = 0.05f;
	public static float ARMOR_DAMAGE_REDUCTION = 25;
	public static float ARMOR_EFFECTIVE_BONUS = 25;
	public static float ARMOR_KINETIC_REDUCTION = 35;
	
	//public static float DAMAGE_TO_COMPONENTS_REDUCTION = 50;
	
	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getArmorBonus().modifyFlat(id, ARMOR_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getArmorBonus().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(ARMOR_BONUS) + " 座舰装甲值";
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
			stats.getArmorDamageTakenMult().modifyMult(id, 1f - ARMOR_DAMAGE_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getArmorDamageTakenMult().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "-" + Math.round(ARMOR_DAMAGE_REDUCTION) + "% 装甲收到的伤害";
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
			stats.getKineticArmorDamageTakenMult().modifyMult(id, 1f - ARMOR_KINETIC_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getKineticArmorDamageTakenMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + Math.round(ARMOR_KINETIC_REDUCTION) + "% 装甲受到的动能伤害";
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
			stats.getEffectiveArmorBonus().modifyMult(id, 1f + (ARMOR_EFFECTIVE_BONUS / 100f));
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getEffectiveArmorBonus().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(ARMOR_EFFECTIVE_BONUS) + "% 装甲的伤害减免效果";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	/*
	public static class Level4 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getEngineDamageTakenMult().modifyMult(id, 1f - DAMAGE_TO_COMPONENTS_REDUCTION / 100f);
			stats.getWeaponDamageTakenMult().modifyMult(id, 1f - DAMAGE_TO_COMPONENTS_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getEngineDamageTakenMult().unmodify(id);
			stats.getWeaponDamageTakenMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(DAMAGE_TO_COMPONENTS_REDUCTION) + "% 武器和引擎受到的伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	*/
	
	
	public static class Level1O implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getMaxArmorDamageReduction().modifyFlat(id, MAX_DAMAGE_REDUCTION_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMaxArmorDamageReduction().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(MAX_DAMAGE_REDUCTION_BONUS * 100) + "% 装甲伤害减免上限";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}

	public static class Level2O implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getMinArmorFraction().modifyFlat(id, MIN_ARMOR_FRACTION_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMinArmorFraction().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(MIN_ARMOR_FRACTION_BONUS * 100f) + "% 剥落装甲最低减伤效果";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	

}
