package second_in_command.skills.automated

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.ids.Strings
import com.fs.starfarer.api.impl.campaign.skills.ElectronicWarfareScript
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ElectronicWarfare : SCBaseSkillPlugin() {

    var PER_SHIP_BONUS = 1.5f

    var CAP_RANGE = 300f
    var CAP_RATE = 3f

    override fun getAffectsString(): String {
        return "所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("舰队中每艘部署的舰船都可提供 $PER_SHIP_BONUS%% 的 电子战强度*", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("可以在 300 距离之外以 3 倍速度更快占领目标点", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        var max = ElectronicWarfareScript.BASE_MAXIMUM.toInt()

        tooltip.addPara("*敌人武器射程会根据你部署舰船的 电子战强度 " +
	"被降低至多 $max%%}。该减益会根据 敌方电子战强度 " +
                "对 己方电子战强度 的比例减弱。" + "对战机无效，影响包括导弹在内的所有武器。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(),
        "$max%")
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        //if (Misc.isAutomated(stats)) {

            stats!!.dynamic.getMod(Stats.ELECTRONIC_WARFARE_FLAT).modifyFlat(id, PER_SHIP_BONUS)

            stats!!.dynamic.getMod(Stats.SHIP_OBJECTIVE_CAP_RANGE_MOD).modifyFlat(id, CAP_RANGE)
            stats.dynamic.getStat(Stats.SHIP_OBJECTIVE_CAP_RATE_MULT).modifyMult(id, CAP_RATE)
        //}
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {
        if (Misc.isAutomated(ship)) {

        }
    }


}