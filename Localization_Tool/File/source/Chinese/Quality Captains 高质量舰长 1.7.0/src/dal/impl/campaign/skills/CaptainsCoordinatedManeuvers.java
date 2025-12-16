package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsCoordinatedManeuvers {
	
	//public static float CP_BONUS = 2f;
	
	public static boolean NAV_BY_LEVELS = true;
	public static boolean NAV_BY_SIZE = false;
	
	public static int PER_FRIG = 1;
	public static int PER_DEST = 1;
	public static int PER_CRSR = 1;
	public static int PER_CAP = 1;
	
	public static float CP_REGEN_FRIGATES = 50f;
	public static float CP_REGEN_DESTROYERS = 25f;
	
	public static class Level0 implements DescriptionSkillEffect {
		
		public String getString() {
			String boonTypes = "";
			String targTypes = "";
			int targN = 0;
			
			if (CaptainsCoordinatedManeuversScript.AFFECTS_SPEED && CaptainsCoordinatedManeuversScript.AFFECTS_MANEUVER) {
				boonTypes = "航速与机动性";
			} else if (CaptainsCoordinatedManeuversScript.AFFECTS_SPEED) {
				boonTypes = "航速";
			} else if (CaptainsCoordinatedManeuversScript.AFFECTS_MANEUVER) {
				boonTypes = "机动性";
			}
			if (CaptainsCoordinatedManeuversScript.APPLY_TO_SHIPS) targN++;
			if (CaptainsCoordinatedManeuversScript.APPLY_TO_FIGHTERS) targN++;
			if (CaptainsCoordinatedManeuversScript.APPLY_TO_MISSILES) targN++;
			
			if (targN >= 3) {
				targTypes = "舰船、战机与导弹";
			} else if (targN == 2) {
				if (CaptainsCoordinatedManeuversScript.APPLY_TO_SHIPS) {
					targTypes += "舰船与";
					if (CaptainsCoordinatedManeuversScript.APPLY_TO_FIGHTERS) targTypes += "战机";
					if (CaptainsCoordinatedManeuversScript.APPLY_TO_MISSILES) targTypes += "导弹";
				} else {
					targTypes = "战机和导弹";
				}
			} else {
				if (CaptainsCoordinatedManeuversScript.APPLY_TO_SHIPS) targTypes += "舰船";
				if (CaptainsCoordinatedManeuversScript.APPLY_TO_FIGHTERS) targTypes += "战机";
				if (CaptainsCoordinatedManeuversScript.APPLY_TO_MISSILES) targTypes += "导弹";
			}
			
			String maxEff = (int)CaptainsCoordinatedManeuversScript.BASE_MAXIMUM + "%";
//			String buoy = "+" + (int)CoordinatedManeuversScript.PER_BUOY + "%";
//			return "Does not apply to fighters. Bonus from each ship only applies to other ships.\n" +
//				   "Nav buoys grant " + buoy + " each, up to a maximum of " + max + " without skill.";
//			return "Nav buoys grant " + buoy + " top speed each, up to a maximum of " + max + " without skills. " +
//					"Does not apply to fighters. Bonus from each ship does not apply to itself.";
			if (boonTypes != "" && targTypes != "") {
				return "*导航效率可提高已部署舰船的" + boonTypes + "，对舰队中的" + targTypes + "生效，最高提高" +
					   	   "" + maxEff + "。";			
			} else {
				return "* 导航效率不提供任何加成或惩罚。";	
			}		
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h, h};
		}
		public String[] getHighlights() {
			String max = (int)CaptainsCoordinatedManeuversScript.BASE_MAXIMUM + "%";
			String jammer = "+" + (int)CaptainsCoordinatedManeuversScript.PER_BUOY + "%";
			return new String [] {jammer, max};
		}
		public Color getTextColor() {
			return null;
		}
	}
	
	public static boolean isFrigateOrDestroyerAndOfficer(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null) return false;
		if (!member.isFrigate() && !member.isDestroyer()) return false;
		
		return !member.getCaptain().isDefault();
	}
	
	public static boolean isOfficer(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null) return false;
		return !member.getCaptain().isDefault();
	}
	
	public static int officerLevel(MutableShipStatsAPI stats) {
		FleetMemberAPI member = stats.getFleetMember();
		if (member == null || member.getCaptain().isDefault()) return 0;
		if (member.isFlagship()) return 5;
		return member.getCaptain().getStats().getLevel();
	}
	
	public static float getClassPts(HullSize hullSize) {
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
	
	public static class Level1A implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			float bonus = 0f;
			if (NAV_BY_LEVELS) {
				bonus += officerLevel(stats);
			}
			if (NAV_BY_SIZE) {
				bonus += getClassPts(hullSize);
			}
			if (bonus > 0f) {
				stats.getDynamic().getMod(Stats.COORDINATED_MANEUVERS_FLAT).modifyFlat(id, bonus);
			}
		}
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.COORDINATED_MANEUVERS_FLAT).unmodify(id);
		}
		public String getEffectDescription(float level) {
			if (NAV_BY_LEVELS && !NAV_BY_SIZE) {
				return "你的舰队的导航效率* 取决于你部署军官的等级之和，你的旗舰视作 5 点";
			} else if (NAV_BY_LEVELS && NAV_BY_SIZE){
				return "你的舰队的导航效率* 取决于你部署军官的等级之和，你的旗舰视作 5 点，\n同时根据每艘部署舰船的船体等级提升 "+ 
						PER_FRIG + "/" + PER_DEST + "/" + PER_CRSR + "/" + PER_CAP 
						+" 点。";
			} else if (NAV_BY_SIZE) {
				return "你的舰队的导航效率* 根据每艘部署舰船的船体等级提升 "+ PER_FRIG + "/" + PER_DEST + "/" + PER_CRSR + "/" + PER_CAP 
						+" 点。";
			}
			return "你的舰队的导航效率只取决于你安装的 导航中继器 船插。";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level1C extends BaseSkillEffectDescription implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			if (isFrigateOrDestroyerAndOfficer(stats)) {
				float bonus = 0f;
				if (hullSize == HullSize.FRIGATE) bonus = CP_REGEN_FRIGATES;
				if (hullSize == HullSize.DESTROYER) bonus = CP_REGEN_DESTROYERS;
				if (bonus > 0f) {
					stats.getDynamic().getMod(Stats.COMMAND_POINT_RATE_FLAT).modifyFlat(id, bonus * 0.01f);
				}
			}
		}
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.COMMAND_POINT_RATE_FLAT).unmodify(id);
		}
		public String getEffectDescription(float level) {
			return null;
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
				TooltipMakerAPI info, float width) {
			init(stats, skill);

			info.addPara("+%s 指挥点恢复速度 (每部署一个护卫舰)，" +
					     "+%s (每部署一个驱逐舰)", 0f, hc, hc,
					     "" + (int) CP_REGEN_FRIGATES + "%",
					     "" + (int) CP_REGEN_DESTROYERS + "%");
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
}
