package dal.impl.campaign.skills;

import java.awt.Color;
import java.util.ArrayList;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.Skills;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsElectronicWarfare {
	
//	public static final float LEVEL_1_BONUS = 0f;
//	public static final float LEVEL_2_BONUS = 5f;
//	public static final float LEVEL_3_BONUS = 5f;
	
	//public static float PER_SHIP_BONUS = 2f;
	public static boolean ECM_FOR_SKILLS = false;
	public static boolean ECM_FOR_LEVELS = true;
	public static boolean ECM_FOR_HULLSIZE = false;
	public static int PER_FRIG = 1;
	public static int PER_DEST = 1;
	public static int PER_CRSR = 1;
	public static int PER_CAP = 1;

	public static float CAP_RANGE = 500f;
	public static float CAP_RATE = 2f;

	
	public static float getBase(HullSize hullSize) {
		float value = 0f;
		switch (hullSize) {
			case CAPITAL_SHIP: value = PER_CAP; break;
			case CRUISER: value = PER_CRSR; break;
			case DESTROYER: value = PER_DEST; break;
			case FRIGATE: value = PER_FRIG; break;
		default:
			break;
		}
		return value;
	}

	public static boolean isOfficer(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null) return false;
		return !member.getCaptain().isDefault();
	}
	
	public static int officerLevel(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null) return 0;
		if (member.getCaptain().isDefault()) return 0;
		if (member.isFlagship()) return 5;
		return member.getCaptain().getStats().getLevel();
	}
	
	public static boolean hasEWARSkills(MutableShipStatsAPI stats) {
		if (stats.getFleetMember() == null || stats.getFleetMember().getCaptain() == null) return false;
		if (stats.getFleetMember().getCaptain().isDefault()) return false;
		if (stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.GUNNERY_IMPLANTS) > 0 
				|| stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.ENERGY_WEAPON_MASTERY) > 0 
				|| stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.ELECTRONIC_WARFARE) > 0) {
			return true;
		}
		return false;
	}
	
	public static int countEWARSkills(MutableShipStatsAPI stats) {
		int count = 0;
		if (stats.getFleetMember() == null || stats.getFleetMember().getCaptain() == null) return 0;
		if (stats.getFleetMember().getCaptain().isDefault()) return 0;
		if (stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.GUNNERY_IMPLANTS) > 0) count++;
		if (stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.ENERGY_WEAPON_MASTERY) > 0) count++;
		if (stats.getFleetMember().getCaptain().getStats().getSkillLevel(Skills.ELECTRONIC_WARFARE) > 0) count++;
		return count;
	}
	
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			String max = (int)CaptainsElectronicWarfareScript.BASE_MAXIMUM + "%";
//			return "*Enemy weapon range is reduced by half of the total ECM rating of the deployed ships, " +
//				"up to a maximum of " + max +
//				". Does not apply to fighters, affects all weapons including missiles.";
//			return "*Reduces enemy weapon range. The total reduction is the lesser of " + max +
//					" and the combined ECM rating for both sides. " +
//					"The side with the lower ECM rating gets a higher penalty. " +
//					"Does not apply to fighters, affects all weapons including missiles.";

//			return "*Enemy weapon range is reduced by the total ECM rating of your deployed ships, "
//					+ "up to a maximum of " + max + ". This penalty is reduced by the ratio "
//					+ "of the enemy ECM rating to yours." +
//					"Does not apply to fighters, affects all weapons including missiles.";

			boolean penGuns = false;
			String subjects = "";
			String penaltyStr = "对";
			ArrayList<String> penTypes = new ArrayList<String>();
			if (CaptainsElectronicWarfareScript.APPLY_TO_TURRETS) {
				if (CaptainsElectronicWarfareScript.APPLIES_TO_RECOIL) { penTypes.add("后坐力"); penGuns = true; }
				if (CaptainsElectronicWarfareScript.APPLIES_TO_RANGE) { penTypes.add("射程"); penGuns = true; }
				if (CaptainsElectronicWarfareScript.APPLIES_TO_AUTOAIM) { penTypes.add("自动开火精度"); penGuns = true; }
				if (CaptainsElectronicWarfareScript.APPLIES_TO_TURRET_TURNRATE) { penTypes.add("炮塔转速"); penGuns = true; }
			}
			if (CaptainsElectronicWarfareScript.APPLY_TO_MISSILES && CaptainsElectronicWarfareScript.APPLIES_TO_MISSILE_TURNRATE) { penTypes.add("导弹机动性"); }

			if (penTypes.size() >= 3) {
				for (int i = 0; i < penTypes.size(); i++) {
					penaltyStr += penTypes.get(i);
					if (i < penTypes.size()-1) penaltyStr += "、";
					if (i == penTypes.size()-2) penaltyStr += "和";
				}
			} else {
				for (int i = 0; i < penTypes.size(); i++) {
					penaltyStr += penTypes.get(i);
					if (i==0 && penTypes.size() > 1) penaltyStr += "和";
				}
			}
			
			if (penaltyStr == "") penaltyStr = "不对任何武器";

			if (CaptainsElectronicWarfareScript.APPLY_TO_SHIPS) { subjects += "对舰船";
				if (CaptainsElectronicWarfareScript.APPLY_TO_FIGHTERS) { subjects += "和战机"; }
			} else if (CaptainsElectronicWarfareScript.APPLY_TO_FIGHTERS) {
				subjects = "只对战机";
			} else {
				subjects = "不对任何单位";
			}
			
			String summary = "" + subjects + "生效，" + penaltyStr + "造成影响。";


			return "友军部署舰船的总电子对抗强度会对敌方的武器性能造成损害，同时根据敌方的电子对抗强度与你方的比例获得抵抗。"
					+ "该效果存在 "
					+ max + " 上限。" + summary;
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h, h, h};
		}
		public String[] getHighlights() {
			String max = (int)CaptainsElectronicWarfareScript.BASE_MAXIMUM + "%";
			String jammer = "+" + (int)CaptainsElectronicWarfareScript.PER_JAMMER + "%";
			return new String [] {jammer, max};
		}
		public Color getTextColor() {
			return null;
		}
	}

	public static class Level0WithNewline extends Level0 {
		public String getString() {
			return "\n" + super.getString();
		}
	}


	public static class Level1A extends BaseSkillEffectDescription implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			float bonus = 0f;
			if (ECM_FOR_HULLSIZE && !BaseSkillEffectDescription.isCivilian(stats)) {
				bonus = getBase(hullSize);
			}
			if (ECM_FOR_LEVELS) {
				bonus += officerLevel(stats);
			}
			if (ECM_FOR_SKILLS) {
				bonus += countEWARSkills(stats);
			}
			if (bonus > 0f) {
				stats.getDynamic().getMod(Stats.ELECTRONIC_WARFARE_FLAT).modifyFlat(id, bonus);
			}
		}
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.ELECTRONIC_WARFARE_FLAT).unmodify(id);
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
				TooltipMakerAPI info, float width) {
			
			init(stats, skill);
			
			if (ECM_FOR_HULLSIZE) {
				info.addPara("根据船体等级，每艘部署舰船提供 " + (int)PER_FRIG +"/"+ (int)PER_DEST +"/"+ (int)PER_CRSR +"/"+ (int)PER_CAP + " 电子对抗强度", hc, 0f);
			}
			if (ECM_FOR_LEVELS) {
				info.addPara("你的舰队的电子对抗强度取决于你部署军官的等级，你的旗舰提供 5% 强度", hc, 0f);
			}
			if (ECM_FOR_SKILLS) {
				info.addPara("你的舰队的电子对抗强度取决于你部署的具备 火控植入 和 能量专精 军官的数量，每个技能提供 1% per 强度", hc, 0f);
			}
			if (!ECM_FOR_LEVELS && !ECM_FOR_HULLSIZE && !ECM_FOR_SKILLS) {
				info.addPara("你的舰队的电子对抗强度取决于你部署舰船安装的 电子对抗套件", hc, 0f);
			}
			info.addSpacer(3f);
		}

		public String getEffectPerLevelDescription() {
			return null;
		}
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_COMBAT_SHIPS;
		}
	}


	public static class Level1B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			if (!BaseSkillEffectDescription.isCivilian(stats)) {
				stats.getDynamic().getMod(Stats.SHIP_OBJECTIVE_CAP_RANGE_MOD).modifyFlat(id, CAP_RANGE);
				stats.getDynamic().getStat(Stats.SHIP_OBJECTIVE_CAP_RATE_MULT).modifyMult(id, CAP_RATE);
			}
		}
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.SHIP_OBJECTIVE_CAP_RANGE_MOD).unmodifyFlat(id);
			stats.getDynamic().getStat(Stats.SHIP_OBJECTIVE_CAP_RATE_MULT).unmodifyMult(id);
		}
		public String getEffectDescription(float level) {
			return "可在更远的距离之外以更快的速度占领战场上的目标点";
		}
		public String getEffectPerLevelDescription() {
			return null;
		}
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
}
